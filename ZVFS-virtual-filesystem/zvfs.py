# implementation of step 01
# 1 byte = 8 bits
import struct  # we need struct to pack/unpack binary formats exactly
import os      # for file and filesystem operations like exists, replace, fsync
import sys     # for command-line argument parsing in the __main__ block
import time    # for timestamps (created field)
from pathlib import Path    # Path makes path operations easier and portable


"""
By default, without < or >, Python uses native alignment. It can add padding bytes, so the struct might actually be bigger 
than expected.
By adding "<" we specifie how bytes are un/packed. < means little-endian: least significant byte comes first
"""
                                 
######################### constants & binary layout ##############################

HEADER_FMT = '<8sBBHHHHHIIIIH26s'       # little-endian, total 64 bytes
HEADER_SIZE = 64                        # header fixed to 64 bytes 
MAGIC = b"ZVFSDSK1"                     # 8-byte magic identifier # used to recognize a valid .zvfs file
VERSION = 1                             # filesystem version # set to 1 per spec
FILE_CAPACITY = 32                      # exactly 32 file entry slots 
ENTRY_SIZE = 64                         # each file entry fixed 64 bytes
DATA_START = HEADER_SIZE + FILE_CAPACITY * ENTRY_SIZE  # 64 + 32*64 = 2112
MAX_OFFSET = 2**32                      # 4 GB limit


class Header:
    def __init__(self, flags=0, file_count=0, deleted_files=0, next_free_offset=None, free_entry_offset=64):
        self.magic = MAGIC                              # fixed
        self.version = VERSION                          # fixed
        self.flags = flags                              # 0 if there is a free spot for a file, 1 otherwise
        self.reserved0 = 0                              # padding
        self.file_count = file_count                    # current nb of active entries (files present and not marked as deleted)
        self.file_capacity = FILE_CAPACITY              # fixed
        self.file_entry_size = ENTRY_SIZE               # fixed
        self.reserved1 = 0                              # padding
        self.file_table_offset = HEADER_SIZE            # fixed, start of file entries
        self.data_start_offset = DATA_START             # fixed, where data region begins
        
        if next_free_offset == None:                    # where to add the next data block, must be 64 aligned 
            self.next_free_offset = DATA_START          # when fs empty -> 2112
        else:                                           # when not empty make sure given offset is within bounds of filesystem!
            if DATA_START <= next_free_offset <= MAX_OFFSET:
                self.next_free_offset = next_free_offset
            else:
                raise ValueError(f"given next_free_offset is not within acceptable bounds (must be between {DATA_START} and {MAX_OFFSET})")

        if free_entry_offset == 0:                      # means there is no free entry left fs is full
            self.free_entry_offset = free_entry_offset
            self.flags = 1
        elif HEADER_SIZE <= free_entry_offset <= DATA_START: # where next free File Entry is (when no files -> start at 64)
            self.free_entry_offset = free_entry_offset  
        else:
            raise ValueError("given free_entry_offset is not whithin acceptable bounds 0 or between {HEADER_SIZE} and {DATA_START})")  

        self.deleted_files = deleted_files              # nb of files marked as deleted
        self.reserved2 = b'\x00' * 26                   # padding


    def pack(self):         # pack header fields into bytes exactly matching HEADER_FMT # used to write header to disk
        return struct.pack(
            HEADER_FMT,
            self.magic,
            self.version,
            self.flags,
            self.reserved0,
            self.file_count,
            self.file_capacity,
            self.file_entry_size,
            self.reserved1,
            self.file_table_offset,
            self.data_start_offset,
            self.next_free_offset,
            self.free_entry_offset,
            self.deleted_files,
            self.reserved2
        )

    def unpack(self, data):         # unpack 64 bytes of header data into the object's attributes # used to read header from disk
        (
            self.magic,
            self.version,
            self.flags,
            self.reserved0,
            self.file_count,
            self.file_capacity,
            self.file_entry_size,
            self.reserved1,
            self.file_table_offset,
            self.data_start_offset,
            self.next_free_offset,
            self.free_entry_offset,
            self.deleted_files,
            self.reserved2
        ) = struct.unpack(HEADER_FMT, data)
        return self

FILE_ENTRY_FORMAT = "<32s I I B B H Q 12s"  # File entry struct format; spaces allowed for readability # <32s I I B B H Q 12s = 32 bytes name + 4 + 4 + 1 + 1 + 2 + 8 + 12 = 64
TYPE = 0

class FileEntry:
    def __init__(self, name=b"", start=0, length=0, flag=0, created=None):

        if isinstance(name, bytes): # decode bytes to string
            name = name.decode("utf-8", errors="ignore")
        
        if start % 64 != 0:    # ensure 64-byte alignment for start offset
           raise ValueError("start offset must be 64-byte aligned")
    
        self.name = name    # type = str (check for name validity is done in addfs)
        self.start = start
        self.length = length
        self.type = TYPE
        self.flag = flag    # 1 if file marked as deleted, 0 otherwise
        self.reserved0 = 0
        self.created = created if created is not None else int(time.time())
        self.reserved1 = b'\x00' * 12

        

    def pack(self):
        # encode name to 32 bytes, null-padded
        name_bytes = self.name.encode("utf-8") if isinstance(self.name, str) else self.name
        name_bytes = name_bytes.ljust(32, b'\x00')  #add null bytes on the right until it is exactly 32 bytes long

        return struct.pack(
            FILE_ENTRY_FORMAT,
            name_bytes,
            self.start,
            self.length,
            self.type,
            self.flag,
            self.reserved0,
            self.created,
            self.reserved1
        )

    def unpack(self, data):
        (
            raw_name,
            self.start,
            self.length,
            self.type,
            self.flag,
            self.reserved0,
            self.created,
            self.reserved1
        ) = struct.unpack(FILE_ENTRY_FORMAT, data)

        # Decode name, stop at null byte
        self.name = raw_name.split(b'\x00', 1)[0].decode('utf-8', errors='ignore')
        return self

    def mark_deleted(self):
        self.flag = 1


######################### helper function ##############################

def addfs_bytes(fs_name, file_name, data_bytes, created_ts=None):
    # helper for dfrgfs -> does the re-adding of active files to filesystem
    # add file into existing filesystem and preserve created_ts
    # was copied from addfs and changed to accepts bytes and created timestamp 

    # assume fs exists
    with open(fs_name, "r+b") as f:
        f.seek(0)
        header = Header().unpack(f.read(HEADER_SIZE))

        if header.flags == 1:   # no more free entries
            print("Error: filesystem entry table is full, cannot add more files.")
            return

        # choose next free entry slot (free_entry_offset points to byte offset of free slot)
        file_entry_index = header.free_entry_offset
        if file_entry_index == 0:   # if free_entry_offset is 0 = fs is full no more data can be added
            print("Error: filesystem is full, cannot add more data.")
            return

        # align data start to 64
        start = ((header.next_free_offset + 63) // 64) * 64

        data_length = len(data_bytes)
        if start + data_length > MAX_OFFSET:
            raise RuntimeError("Data is too big for this filesystem")

        # write data and padding
        f.seek(start)
        f.write(data_bytes)                                                         # THIS IS DIFFERENT TO ADDFS
        padded_length = ((data_length + 63) // 64) * 64
        if padded_length > data_length:
            f.write(b'\x00' * (padded_length - data_length))

        # create file entry with provided created timestamp if given
        new_entry = FileEntry(
            name=file_name,
            start=start,
            length=data_length,
            flag=0,
            created=(created_ts if created_ts is not None else int(time.time()))    # THIS IS DIFFERENT TO ADDFS
        )

        # write entry into file table
        f.seek(file_entry_index)
        f.write(new_entry.pack())

        # update header values
        header.file_count += 1
        # compute next free entry offset
        next_entry_offset = file_entry_index + ENTRY_SIZE
        header.free_entry_offset = next_entry_offset if next_entry_offset < header.data_start_offset else 0
        header.next_free_offset = start + padded_length
        header.flags = 1 if header.free_entry_offset == 0 else 0

        # write header back
        f.seek(0)
        f.write(header.pack())
        f.flush()
        os.fsync(f.fileno())


######################### operations ##############################

def mkfs(fs_name):              # make a new filesystem
    if os.path.exists(fs_name) :# check filesystem doesn't already exist
        print(f"Error: {fs_name} already exists.")
        return

    # create empty header
    header = Header()

    with open(fs_name, "wb") as f:
        f.write(header.pack())
        f.write(b"\x00" * (FILE_CAPACITY * ENTRY_SIZE)) # body: write empty file entries (32 entries of 64 bytes)

    print(f"Created empty filesystem: {fs_name}")


def gifs(fs_name):              # get info of the filesystem
    if not os.path.exists(fs_name): # check if filesystem exists
        print(f"Error: {fs_name} doesn't exist.")
        return

    with open(fs_name, "rb") as f:
        # read header
        header = Header().unpack(f.read(HEADER_SIZE))

        files_present = header.file_count   # number of files present (non deleted) 
        free_entries = int((header.data_start_offset - header.free_entry_offset)/64) # remaining entries for new files (excluding deleted files) -> nb of actual empty spots
                    # free_entries is the total nb of empty spots (spots with no active nor marked as deleted files), we don't want to allow overwritting on "marked as deleted" files 
                    # this way the user sees how many really free spots are left and if the filesystem has too many marked as deleted files he would first defragmentate before adding a new file       
        
        # read all file entries to calculate total size
        total_size = 0
        f.seek(header.file_table_offset)  # make sure to start at the file entry table
        for _ in range(header.file_capacity):
            entry_data = f.read(ENTRY_SIZE)
            entry = FileEntry().unpack(entry_data)
            if entry.length > 0:
                total_size += entry.length

        print(f"Filesystem: {fs_name}")
        print(f"Files present: {files_present}")
        print(f"Free entries: {free_entries}") 
        print(f"Deleted files: {header.deleted_files}")
        print(f"Total space used: {total_size} bytes")


def addfs(fs_name, file_path):  # add file to filesystem
# adds a file from the host computer into the .zvfs filesystem
# throws an error if file already exists in filesystem
# finds an available entry slot, writes the file's bytes into the data region (aligned to 64 bytes), 
# updates the header, and creates a new file entry describing the stored file.
    
    if not os.path.exists(fs_name):     # check if filesystem exists
        print(f"Error: filesystem {fs_name} doesn't exist.")
        return
    host_file = Path(file_path)         # convert host file path -> a Path object for easier handling
    if not host_file.exists():          # check whether the host file actually exists
        print(f"Error: host file {file_path} does not exist.")  # show error if host file is missing
        return                          # stop function if file not found

    data = host_file.read_bytes()       # read all bytes from the host file
    data_length = len(data)             # get the real data length without padding
    
    file_name = os.path.basename(file_path) # get file name and check that length is valid
    name_bytes = file_name.encode("utf-8")
    if len(name_bytes) == 0:
        print("Error: file name must contain at least one character.")
        return
    if len(name_bytes) > 31:
        print("Error: file name is too long in bytes (max 31 bytes in UTF-8).")
        return

    with open(fs_name, "r+b") as f:  # open the filesystem file for reading & writing in binary mode
        f.seek(0)  # jump to the beginning of the filesystem
        header = Header().unpack(f.read(HEADER_SIZE))   # read and unpack the header into a Header object

        # check that file we want to add doesn't already exist in filesystem
        for i in range(header.file_capacity):           
            f.seek(header.file_table_offset + i * ENTRY_SIZE)
            raw = f.read(ENTRY_SIZE)
            entry = FileEntry().unpack(raw)

            if entry.flag == 0 and entry.name == file_name and entry.length > 0:
                print(f"Error: file '{file_name}' already exists in filesystem.")
                return
        
        # check if there is a free spot for a file entry
        if header.flags == 1:   # no more free entries
            print("Error: filesystem entry table is full, cannot add more files.")
            return
        
        # find first free entry in filesystem table 
        file_entry_index = header.free_entry_offset
        if file_entry_index == 0:   # if free_entry_offset is 0 = fs is full no more data can be added
            print("Error: filesystem is full, cannot add more data.")
            return

        # calculate where file data should be written (next 64-aligned offset)
        start = ((header.next_free_offset + 63) // 64) * 64 # works even if already aligned

        # check that data to add is not longer than max allowed size
        if start + data_length > MAX_OFFSET: # 4GB
            print("Data is too big for this filesystem")
            return
        
        f.seek(start)  # move pointer to where the file data will be stored
        f.write(data)  # write the file data bytes into the filesystem

        padded_length = ((data_length + 63) // 64) * 64         # compute padded size to remain 64-byte aligned
        if padded_length > data_length:                         # check if padding is needed
            f.write(b'\x00' * (padded_length - data_length))    # write zero padding bytes

        # create and write new file entry
        new_entry = FileEntry(          # create a new file entry object
            name=file_name,             # store only the filename (not full path)
            start=start,                # location where the file data starts
            length=data_length,         # actual file length (without padding)
            flag=0,                     # file is active (not deleted)
            created=int(time.time())    # store creation timestamp
        )  # end FileEntry constructor
        f.seek(file_entry_index)        # move pointer to file entry slot
        f.write(new_entry.pack())       # write packed file entry into filesystem

        # update header
        header.file_count += 1          # increase the number of active files
        header.free_entry_offset = file_entry_index + 64 # move free_entry_offset to next slot for next file entry
        header.next_free_offset = start + padded_length  # move next_free_offset to end of padded data
        if header.free_entry_offset >= DATA_START:       # fs has no free file entries left
            header.flags = 1
            header.free_entry_offset = 0
        if header.next_free_offset > MAX_OFFSET:         # fs is full (4GB)
            print(f"After adding file {file_name} the filesystem is now full")
            header.free_entry_offset = 0
            return

        f.seek(0)                       # return pointer to beginning
        f.write(header.pack())          # write updated header back to filesystem
        f.flush()                       # flush Python buffer
        os.fsync(f.fileno())            # ensure data is flushed to disk

    print(f"Added file: {file_name} ({data_length} bytes), information on that file is at entry {file_entry_index}, the data is located at offset {start}")  


def getfs(fs_name, file_name):  # extract file from filesystem to disc
# extracts a file stored inside the .zvfs filesystem back to the host computer
# It searches the file-entry table for the requested filename, reads the file's data from the filesystem 
# using its stored offset and length, and writes it into a new file on the host

    if not os.path.exists(fs_name):  # ensure filesystem exists
        print(f"Error: filesystem {fs_name} not found.")  # show error if missing
        return  # stop function

    with open(fs_name, "rb") as f:  # open filesystem for reading
        f.seek(0)  # go to start
        header = Header().unpack(f.read(HEADER_SIZE))  # load and unpack the header

        if header.magic != MAGIC:
            print("Error: invalid filesystem format.")
            return

        found_entry = None  # will store the matching file entry

        for i in range(header.file_capacity):  # scan through all file entries
            entry_offset = HEADER_SIZE + i * ENTRY_SIZE  # compute offset for entry i
            f.seek(entry_offset)  # move pointer to entry
            entry = FileEntry().unpack(f.read(ENTRY_SIZE))  # read and unpack entry

            if entry.name == file_name:
                found_entry = entry  # store matching entry
                break  # stop search

        if found_entry is None:  # if file not found
            print(f"Error: File '{file_name}' not found in filesystem.")  # print error
            return  # stop function
        
        if found_entry.flag == 1:
            print(f"Warning: '{file_name}' is marked as deleted — recovering anyway.")

        f.seek(found_entry.start)  # go to the start of the file’s data region
        data = f.read(found_entry.length)  # read only the exact file length (exclude padding)

    out_path = Path(found_entry.name)  # construct output path using file entry name
    if out_path.exists():
        print(f"Warning: file {out_path} already exists on host, it will be overwritten.")

    with open(out_path, "wb") as out:  # open new host file for writing
        out.write(data)  # write extracted bytes to host system

    print(f"Extracted file: {found_entry.name} ({found_entry.length} bytes) from {fs_name}")


def rmfs(fs_name, file_name):   # mark file of filesystem as deleted
    # update flag, file_count changes as well (should return nb of active files and not marked as deleted)

    if not os.path.exists(fs_name):
        print(f"Error: filesystem {fs_name} doesn't exist.")
        return

    with open(fs_name, "rb+") as f: # open filesystem for reading + writing
        header = Header().unpack(f.read(HEADER_SIZE))
        
        f.seek(header.file_table_offset) # seek to the file entry table

        found = False
        for i in range(header.file_capacity):
            pos = f.tell()                          # current position before reading, saves position of current start of file entry
            entry_data = f.read(ENTRY_SIZE)         # this will move the pointer
            entry = FileEntry().unpack(entry_data)

            if entry.name == file_name and entry.flag == 0:
                entry.flag = 1                      # mark as deleted
                f.seek(pos)                         # go back to start of file entry
                f.write(entry.pack())               # write updated entry back

                header.file_count -= 1              # update header
                header.deleted_files += 1

                f.seek(0)                           # write header back to disk
                f.write(header.pack())

                print(f"Removed {file_name} from filesystem.")
                found = True
                break

        if not found:
            print(f"Error: file {file_name} not found in filesystem.")


def lsfs(fs_name):              # list of all files stored in virtual filesystem
    if not os.path.exists(fs_name):                         # check if the file actually exists on disk
        print(f"Error: Filesystem '{fs_name}' not found.")
        return                                              # stop function
    
    with open(fs_name, "rb") as f:                          # open file, read in binary 
        
        f.seek(0)                                           # read the header, position 0 
        header_data = f.read(HEADER_SIZE)                   # read exactly 64 bytes (header size)
        header = Header().unpack(header_data)               # convert binary data to Header object
        
        # header tells num files in system, 32 slots
        print(f"Files in virtual filesystem: {fs_name}")    #displaying list header
        print("=" * 60)                                     # visual separator line
        print(f"{'Filename':<20} {'Size (bytes)':<12} {'Created On':<20}")
        print("-" * 60)                                     # another separator

        found_files = False  # Flag to track if we found any files
        files_listed = 0     # Counter for actual files displayed
        
        # Loop through ALL 32 possible file entry slots
        for slot_number in range(header.file_capacity):
            
            # Calculate where this file entry is located in the file:
            # Header (64 bytes) + (slot number × entry size 64 bytes)
            entry_offset = HEADER_SIZE + (slot_number * ENTRY_SIZE)
            
            f.seek(entry_offset)
            
            # read 64 bytes 
            entry_data = f.read(ENTRY_SIZE)
            
            # convert the binary data into a FileEntry object we can work with, unpack
            entry = FileEntry().unpack(entry_data)
            
            # now checking real active file: not marked as deleted (entry.flag == 0), not a name, not just space
            if (entry.flag == 0 and                    # Not deleted
                entry.name and                         # name exists
                entry.name.strip() and                 # name isn't just spaces
                entry.length >= 0):                    # has valid size
                
                found_files = True    # found at least one file
                files_listed += 1     # counter
                
                # displaying 
                created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry.created))
                
                print(f"{entry.name:<20} {entry.length:<12} {created_time:<20}")
        
        if not found_files:      # if no files were found: 
            print("No active files found in the filesystem.")
            print("This filesystem is empty or all files are marked as deleted.")
        else:
            # summary
            print("-" * 60)
            print(f"Total files listed: {files_listed}")
            print(f"Filesystem capacity: {header.file_capacity} slots")
            print(f"Free slots remaining: {int((header.data_start_offset - header.free_entry_offset)/64)}") # should print nb of actually empty slots (marked as deleted IS NOT an empty slot)


def dfrgfs(fs_name):            # definitive deletion of marked files
    # defragment by extracting active files, resetting the filesystem, and re-adding active files
    # prints how many files were removed and how many bytes freed (counting padded bytes)

    if not os.path.exists(fs_name):
        print(f"Error: filesystem '{fs_name}' does not exist.")
        return

    # read header and entries (read-only)
    with open(fs_name, "rb") as f:
        header = Header().unpack(f.read(HEADER_SIZE))

        all_entries = []
        for i in range(header.file_capacity):
            f.seek(header.file_table_offset + i * ENTRY_SIZE)
            raw = f.read(ENTRY_SIZE)
            entry = FileEntry().unpack(raw)
            all_entries.append(entry)

        # collect active entries and deleted ones
        active_infos = []  # list of tuples (name, bytes, time created)
        deleted_count = 0
        bytes_freed = 0

        for e in all_entries:
            if e.flag == 1:                 # deleted entry — add file size to freed bytes
                file_data_freed = e.length 
                bytes_freed += file_data_freed 
                deleted_count += 1

            elif e.name and e.length > 0:   # active file: read its data
                f.seek(e.start)
                data = f.read(e.length)
                active_infos.append((e.name, data, e.created))

    if deleted_count == 0:
        print("No deleted files to remove. Filesystem already clean.")
        return

    print(f"Found {deleted_count} file(s) marked for deletion")
    print(f"Found {len(active_infos)} active file(s)")

    # reset filesystem in-place: create new empty header and zero the entry table region
    empty_header = Header()
    with open(fs_name, "r+b") as f:
        # overwrite old header with new empty header
        f.seek(0)
        f.write(empty_header.pack())
        # zero the file entry table region
        f.seek(empty_header.file_table_offset)
        f.write(b'\x00' * (FILE_CAPACITY * ENTRY_SIZE))
        f.flush()
        os.fsync(f.fileno())

    # re-add active files using addfs_bytes (preserves creation time)
    readded = 0
    for name, data_bytes, created_ts in active_infos:
        addfs_bytes(fs_name, name, data_bytes, created_ts)
        readded += 1

    # read new final header to report status after dfrgfs
    with open(fs_name, "rb") as f:
        final_header = Header().unpack(f.read(HEADER_SIZE))

    print("Defragmentation complete!")
    print(f"Files removed: {deleted_count}")
    print(f"Bytes freed (file data not counting padding): {bytes_freed}")
    print(f"Active files after defragmentation: {final_header.file_count}")
    print(f"Next free data offset: {final_header.next_free_offset}")

        
def catfs(fs_name, file_name):  # print the contents of a file stored in the .zvfs filesystem to the console
    
    if not os.path.exists(fs_name):
        print(f"Error: filesystem '{fs_name}' does not exist.")
        return

    with open(fs_name, "rb") as f:
       
        # Read header
        header = Header().unpack(f.read(HEADER_SIZE))
        
        found_entry = None

        # Search for file in file entries
        for i in range(header.file_capacity):
            entry_offset = HEADER_SIZE + i * ENTRY_SIZE
            f.seek(entry_offset)
            entry = FileEntry().unpack(f.read(ENTRY_SIZE))
            
            if entry.name == file_name and entry.flag == 0:  # active file only
                found_entry = entry
                break

        if found_entry is None:
            print(f"Error: File '{file_name}' not found in filesystem.")
            return

        # Read the actual file data
        f.seek(found_entry.start)
        data = f.read(found_entry.length)

        # Print raw bytes as string, no decode 
        print(f"Contents of '{file_name}':\n")
        print(data.decode(errors='ignore'))  # ignore any invalid bytes, safe for beginners


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python zvfs.py <command> <filesystem> [args...]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "mkfs":
        mkfs(sys.argv[2])

    if command == "gifs":
        gifs(sys.argv[2])

    if command == "addfs":
        if len(sys.argv) < 4:
            print("Usage: python zvfs.py addfs <filesystem> <file_to_add>")
            sys.exit(1)
        addfs(sys.argv[2], sys.argv[3])

    if command == "getfs":
        if len(sys.argv) < 4:
            print("Usage: python zvfs.py getfs <filesystem> <file_to_extract>")
            sys.exit(1)
        getfs(sys.argv[2], sys.argv[3])

    if command == "rmfs":
        if len(sys.argv) < 4:
            print("Usage: python zvfs.py rmfs <filesystem> <file_to_extract>")
            sys.exit(1)
        rmfs(sys.argv[2], sys.argv[3])
    
    if command == "catfs":
        if len(sys.argv) < 4:
            print("Usage: python zvfs.py catfs <filesystem> <file_to_print>")
            sys.exit(1)
        catfs(sys.argv[2], sys.argv[3])
    
    if command == "lsfs":
        if len(sys.argv) < 3:
            print("Usage: python zvfs.py lsfs <filesystem>")
            sys.exit(1)
        lsfs(sys.argv[2])
    
    if command == "dfrgfs":
        if len(sys.argv) < 3:
            print("Usage: python zvfs.py dfrgfs <filesystem>")
            sys.exit(1)
        dfrgfs(sys.argv[2])
        
        