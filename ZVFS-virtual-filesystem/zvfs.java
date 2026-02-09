// implementation of step 02
// 1 byte = 8 bits, short 16 bits (2 bytes), int = 32 bits(4 bytes)
// all methods have to be static so we can call them from main otherwise we get : Cannot make a static reference to the non-static method from the type zvfs

import java.io.*;               // for exceptions
import java.nio.ByteBuffer;     // for packing and unpacking
import java.nio.ByteOrder;      // for packing and unpacking -> reading the bytes in little endian
import java.nio.file.Files;


public class zvfs {
    // ==== CONSTANTS ====
    static final int HEADER_SIZE = 64;
    static final int FILE_CAPACITY = 32;
    static final int ENTRY_SIZE = 64;
    static final int DATA_START = HEADER_SIZE + FILE_CAPACITY * ENTRY_SIZE;   // 64 + 2048 = 2112
    static final long MAX_OFFSET = (1L << 32);
    static final byte[] MAGIC = "ZVFSDSK1".getBytes();   // 8 bytes
    static final int VERSION = 1;


    // ----- mkfs -----
    public static void mkfs(String fsName) throws IOException {
        File f = new File(fsName);
        if (f.exists()) {               // check filesystem doesn't already exist
            System.out.println("Error: " + fsName + " already exists.");
            return;
        }

        // build empty header
        Header header = new Header();
        header.flags = 0;
        header.fileCount = 0;
        header.deletedFiles = 0;

        // RandomAccessFile: a Java class that enables read and write binary data at any position in a file
        // rw: read and write 
        try (RandomAccessFile raf = new RandomAccessFile(f, "rw")) { // try is mandatory: ensures file is always closed, no matter what
            // write packed header (64 bytes)
            raf.seek(0);                // move to start of file
            raf.write(header.pack());       // write header

            // write 32 empty file entries (32 * 64 bytes)
            byte[] emptyEntry = new byte[ENTRY_SIZE];
            raf.seek(HEADER_SIZE);          // move pointer to start of file table
            for (int i = 0; i < FILE_CAPACITY; i++) {
                raf.write(emptyEntry);
            }

        } catch (IOException e) {System.out.println("Error while creating filesystem: ");}

        System.out.println("Created empty filesystem: " + fsName);
    }


    // ----- addfs -----
    public static void addfs(String fsName, String filePath) throws IOException {

        File fs = new File(fsName);
        if (!fs.exists()) {                 // check filesystem exists
            System.out.println("Error: filesystem " + fsName + " doesn't exist.");
            return;
        }

        File hostFile = new File(filePath);
        if (!hostFile.exists()) {           // check file exists
            System.out.println("Error: host file " + filePath + " does not exist.");
            return;
        }

        // read file data and get length
        byte[] data = java.nio.file.Files.readAllBytes(hostFile.toPath());
        int dataLength = data.length;
        
        // read file name and convert to bytes
        String fileName = hostFile.getName();
        byte[] nameBytes = fileName.getBytes();

        // check name is valid
        if (nameBytes.length == 0) {
            System.out.println("Error: file name must not be empty.");
            return;
        }
        if (nameBytes.length > 31) {
            System.out.println("Error: file name is too long (max 31 bytes).");
            return;
        }
        // RandomAccessFile: a Java class that enables read and write binary data at any position in a file
        // rw: read and write 
        RandomAccessFile raf = new RandomAccessFile(fs, "rw");

        // read header
        raf.seek(0);                                // move to start of file system to read header
        byte[] hdrBytes = new byte[HEADER_SIZE];        // allocate array to hold raw header bytes
        raf.readFully(hdrBytes);                        // read 64 bytes from file into array
        Header header = new Header();                   // create new empty header object
        ByteBuffer hdrBuf = ByteBuffer.wrap(hdrBytes);  // wrap bytes in a ByteBuffer for easier structured reading
        hdrBuf.order(ByteOrder.LITTLE_ENDIAN);          // ensure multi-byte numbers are interpreted in little-endian order
        header.unpack(hdrBytes);                        // fill Header object fields from the raw bytes

        // unpack each entry and check for duplicate
        for (int i = 0; i < FILE_CAPACITY; i++) {
            raf.seek(header.fileTableOffset + i * ENTRY_SIZE);
            byte[] entryData = new byte[ENTRY_SIZE];
            raf.readFully(entryData);
            FileEntry entry = new FileEntry().unpack(entryData);

            if (entry.flag == 0 && entry.name.equals(fileName) && entry.length > 0) {
                System.out.println("Error: file '" + fileName + "' already exists in filesystem.");
                raf.close();
                return;
            }
        }

        // check if there is a free slot
        if (header.flags == 1) {    // table is full
            System.out.println("Error: filesystem entry table is full.");
            raf.close();
            return;
        }

        int fileEntryOffset = header.freeEntryOffset;
        if (fileEntryOffset == 0) { // data storage is full
            System.out.println("Error: filesystem is full (no data slots left).");
            raf.close();
            return;
        }

        // compute 64-aligned start offset for data
        int start = ((header.nextFreeOffset + 63) / 64) * 64;

        if ((long) start + dataLength > MAX_OFFSET) {
            System.out.println("Data is too large.");
            raf.close();
            return;
        }

        // write file data
        raf.seek(start);
        raf.write(data);

        // pad to 64 bytes
        int paddedLength = ((dataLength + 63) / 64) * 64;
        if (paddedLength > dataLength) {
            raf.write(new byte[paddedLength - dataLength]);
        }

        // create new FileEntry
        long now = System.currentTimeMillis() / 1000; // Python uses seconds
        FileEntry entry = new FileEntry(fileName, start, dataLength, (byte)0, now);

        // write entry to table
        raf.seek(fileEntryOffset);
        raf.write(entry.pack());

        // update header
        header.fileCount++;
        header.freeEntryOffset = fileEntryOffset + 64;
        header.nextFreeOffset = start + paddedLength;

        if (header.freeEntryOffset >= DATA_START) {
            header.flags = 1;
            header.freeEntryOffset = 0;
        }

        // write updated header
        raf.seek(0);
        raf.write(header.pack());

        raf.close();

        System.out.println("Added file: " + fileName + " (" + dataLength + " bytes)");
        System.out.println("Entry at " + fileEntryOffset + ", data at offset " + start);
    }


    // ----- gifs -----
    public static void gifs(String fsName) {
        File fsFile = new File(fsName);
        if (!fsFile.exists()) {
            System.out.println("Error: " + fsName + " doesn't exist.");
            return;
        }

        try (RandomAccessFile raf = new RandomAccessFile(fsFile, "r")) { // read only

            // read and unpack header
            raf.seek(0); // move to start of file
            byte[] headerBytes = new byte[HEADER_SIZE];
            raf.readFully(headerBytes); // read exactly HEADER_SIZE bytes

            Header header = new Header();
            header.unpack(headerBytes);

            int filesPresent = header.fileCount;

            // free_entries = (data_start_offset - free_entry_offset) / 64
            int freeEntries = (header.dataStartOffset - header.freeEntryOffset) / ENTRY_SIZE;

            // calculate total size of all present files
            long totalSize = 0;

            // move to the start of the file table
            raf.seek(header.fileTableOffset);

            byte[] entryBytes = new byte[ENTRY_SIZE];

            for (int i = 0; i < header.fileCapacity; i++) {
                raf.readFully(entryBytes); // read exactly ENTRY_SIZE bytes

                FileEntry entry = new FileEntry();
                entry.unpack(entryBytes);

                if (entry.length > 0) {
                    totalSize += entry.length;
                }
            }

            // print info
            System.out.println("Filesystem: " + fsName);
            System.out.println("Files present: " + filesPresent);
            System.out.println("Free entries: " + freeEntries);
            System.out.println("Deleted files: " + header.deletedFiles);
            System.out.println("Total space used: " + totalSize + " bytes");

        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    // --- getfs ---
    public static void getfs(String filesystemName, String filename) throws IOException {
        // Check if the virtual filesystem file exists
        File fsFile = new File(filesystemName);
        if (!fsFile.exists()) {
            System.out.println("Error: filesystem " + filesystemName + " doesn't exist.");
            return;
        }

        // Check if the target file already exists on host 
        File hostFile = new File(filename);
        if (hostFile.exists()) {
            System.out.println("Warning: host file " + filename + " already exists and will be overwritten.");
        }

        try (RandomAccessFile raf = new RandomAccessFile(fsFile, "r")) {
            // Read the filesystem header
            byte[] headerData = new byte[Header.HEADER_SIZE];
            raf.seek(0);                    // move to the beginning of the file
            raf.readFully(headerData);          // read header bytes
            Header header = new Header();
            header.unpack(headerData);          // convert bytes into Header fields

            boolean found = false;              // flag to indicate if the file is found

            // Loop through all file entries in the file table
            for (int i = 0; i < header.fileCapacity; i++) {
                raf.seek(header.fileTableOffset + i * FileEntry.ENTRY_SIZE); // move to current entry
                byte[] entryData = new byte[FileEntry.ENTRY_SIZE];
                raf.readFully(entryData);
                FileEntry entry = new FileEntry().unpack(entryData);

                // Check if the entry matches the requested filename and is not deleted
                if (entry.name.equals(filename) && entry.flag == 0) {
                    found = true;

                    // Read the file data from its start offset
                    byte[] fileData = new byte[entry.length];
                    raf.seek(entry.start);
                    raf.readFully(fileData);

                    // Write the extracted file back to host filesystem
                    Files.write(hostFile.toPath(), fileData);

                    System.out.println("Extracted file: " + filename + " (" + entry.length + " bytes) from " + filesystemName);
                    break;
                }
            }

            if (!found) {
                System.out.println("Error: file '" + filename + "' not found in filesystem or marked as deleted.");
            }

        } catch (IOException e) {
            System.out.println("Error accessing filesystem: ");
            e.printStackTrace();
        }
    }


    // --- rmfs ---
    public static void rmfs(String filesystemName, String filename) throws IOException {
        // Check if the virtual filesystem exists
        File fsFile = new File(filesystemName);
        if (!fsFile.exists()) {
            System.out.println("Error: filesystem " + filesystemName + " doesn't exist.");
            return;
        }

        try (RandomAccessFile raf = new RandomAccessFile(fsFile, "rw")) {
            // Read the filesystem header
            byte[] headerData = new byte[Header.HEADER_SIZE];
            raf.seek(0);                  // move to the start of the file
            raf.readFully(headerData);
            Header header = new Header();
            header.unpack(headerData);        // parse the header

            boolean found = false;            // flag to indicate if file was found

            // Loop through all file entries in the filesystem
            for (int i = 0; i < header.fileCapacity; i++) {
                raf.seek(header.fileTableOffset + i * FileEntry.ENTRY_SIZE); // move to the entry
                byte[] entryData = new byte[FileEntry.ENTRY_SIZE];
                raf.readFully(entryData);
                FileEntry entry = new FileEntry().unpack(entryData);

                // Check if this entry matches the requested file and is active
                if (entry.name.equals(filename) && entry.flag == 0) {
                    found = true;

                    // Mark the file as deleted by setting the flag
                    entry.flag = 1;
                    raf.seek(header.fileTableOffset + i * FileEntry.ENTRY_SIZE); // move back to entry
                    raf.write(entry.pack()); // overwrite the entry with deletion flag

                    // Update header's deleted file count
                    header.deletedFiles++;
                    raf.seek(0); // move back to start to update header
                    raf.write(header.pack());

                    System.out.println("Removed file: " + filename + " from filesystem.");
                    break;
                }
            }

            if (!found) {
                System.out.println("Error: file '" + filename + "' not found in filesystem or already deleted.");
            }

        } catch (IOException e) {
            System.out.println("Error accessing filesystem: ");
            e.printStackTrace();
        }
    }


    // --- lsfs ---
    public static void lsfs(String fsName) throws IOException {
        File fsFile = new File(fsName);
        if (!fsFile.exists()) {
            System.out.println("Error: " + fsName + " doesn't exist.");
            return;
        }

        try (RandomAccessFile raf = new RandomAccessFile(fsFile, "r")) {
            // Read header
            byte[] headerData = new byte[HEADER_SIZE];
            raf.seek(0);
            raf.readFully(headerData);
            Header header = new Header();
            header.unpack(headerData);

            System.out.println("Files in virtual filesystem: " + fsName);
            System.out.println("=".repeat(60));
            System.out.printf("%-20s %-12s %-20s%n", "Filename", "Size (bytes)", "Created On");
            System.out.println("-".repeat(60));

            int filesListed = 0;
            boolean foundFiles = false;

            // Loop through all 32 file entry slots
            for (int i = 0; i < header.fileCapacity; i++) {
                raf.seek(header.fileTableOffset + i * ENTRY_SIZE);
                byte[] entryData = new byte[ENTRY_SIZE];
                raf.readFully(entryData);
                
                FileEntry entry = new FileEntry();
                entry.unpack(entryData);

                // Check if this is an active file (not deleted, has name and length)
                if (entry.flag == 0 && entry.name != null && !entry.name.trim().isEmpty() && entry.length > 0) {
                    foundFiles = true;
                    filesListed++;
                    
                    // Convert timestamp to readable format
                    java.util.Date date = new java.util.Date(entry.created * 1000L);
                    java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
                    String createdTime = sdf.format(date);
                    
                    System.out.printf("%-20s %-12d %-20s%n", 
                        (entry.name.length() > 20 ? entry.name.substring(0, 17) + "..." : entry.name),
                        entry.length, 
                        createdTime);
                }
            }

            if (!foundFiles) {
                System.out.println("No active files found in the filesystem.");
                System.out.println("This filesystem is empty or all files are marked as deleted.");
            } else {
                System.out.println("-".repeat(60));
                System.out.println("Total files listed: " + filesListed);
                System.out.println("Filesystem capacity: " + header.fileCapacity + " slots");
                
                // Calculate free slots (empty slots, not including deleted ones)
                int freeSlots = 0;
                for (int i = 0; i < header.fileCapacity; i++) {
                    raf.seek(header.fileTableOffset + i * ENTRY_SIZE);
                    byte[] entryData = new byte[ENTRY_SIZE];
                    raf.readFully(entryData);
                    FileEntry entry = new FileEntry();
                    entry.unpack(entryData);
                    
                    if ((entry.name == null || entry.name.trim().isEmpty()) && entry.flag == 0) {
                        freeSlots++;
                    }
                }
                System.out.println("Free slots remaining: " + freeSlots);
            }
        }
    }


    // --- catfs ---
    public static void catfs(String fsName, String fileName) throws IOException {
        File fsFile = new File(fsName);
        if (!fsFile.exists()) {
            System.out.println("Error: " + fsName + " doesn't exist.");
            return;
        }

        try (RandomAccessFile raf = new RandomAccessFile(fsFile, "r")) {
            // Read header
            byte[] headerData = new byte[HEADER_SIZE];
            raf.seek(0);
            raf.readFully(headerData);
            Header header = new Header();
            header.unpack(headerData);

            FileEntry foundEntry = null;
            
            // Search for the file in file entries
            for (int i = 0; i < header.fileCapacity; i++) {
                raf.seek(header.fileTableOffset + i * ENTRY_SIZE);
                byte[] entryData = new byte[ENTRY_SIZE];
                raf.readFully(entryData);
                
                FileEntry entry = new FileEntry();
                entry.unpack(entryData);
                
                if (entry.name != null && entry.name.equals(fileName) && entry.flag == 0) {
                    foundEntry = entry;
                    break;
                }
            }

            if (foundEntry == null) {
                System.out.println("Error: File '" + fileName + "' not found in filesystem.");
                return;
            }

            // Read the file data
            raf.seek(foundEntry.start);
            byte[] fileData = new byte[foundEntry.length];
            raf.readFully(fileData);

            // Print to console
            System.out.println("Contents of '" + fileName + "':");
            System.out.println("=".repeat(60));
            
            // Try to print as text (ignore binary files)
            try {
                String content = new String(fileData, "UTF-8");
                System.out.println(content);
            } catch (Exception e) {
                System.out.println("[Binary file - cannot display as text]");
                System.out.println("File size: " + foundEntry.length + " bytes");
            }
            
            System.out.println("=".repeat(60));
        }
    }
    

    // --- dfrgfs ---
    public static void dfrgfs(String fsName) throws IOException {
        File fsFile = new File(fsName);
        if (!fsFile.exists()) {
            System.out.println("Error: " + fsName + " doesn't exist.");
            return;
        }

        // First, read all active files and their data
        java.util.List<FileData> activeFiles = new java.util.ArrayList<>();
        int deletedCount = 0;
        long bytesFreed = 0;

        try (RandomAccessFile raf = new RandomAccessFile(fsFile, "r")) {
            // Read header
            byte[] headerData = new byte[HEADER_SIZE];
            raf.seek(0);
            raf.readFully(headerData);
            Header header = new Header();
            header.unpack(headerData);

            // Collect all active files and count deleted ones
            for (int i = 0; i < header.fileCapacity; i++) {
                raf.seek(header.fileTableOffset + i * ENTRY_SIZE);
                byte[] entryData = new byte[ENTRY_SIZE];
                raf.readFully(entryData);
                
                FileEntry entry = new FileEntry();
                entry.unpack(entryData);

                if (entry.flag == 1 && entry.name != null && !entry.name.trim().isEmpty()) {
                    // This is a deleted file
                    deletedCount++;
                    bytesFreed += entry.length;
                } else if (entry.flag == 0 && entry.name != null && !entry.name.trim().isEmpty() && entry.length > 0) {
                    // This is an active file - read its data
                    raf.seek(entry.start);
                    byte[] fileData = new byte[entry.length];
                    raf.readFully(fileData);
                    
                    activeFiles.add(new FileData(entry.name, fileData, entry.created));
                }
            }
        }

        if (deletedCount == 0) {
            System.out.println("No deleted files to remove. Filesystem already clean.");
            return;
        }

        System.out.println("Found " + deletedCount + " file(s) marked for deletion");
        System.out.println("Found " + activeFiles.size() + " active file(s) to keep");

        // Create a temporary file for the defragmented filesystem
        File tempFile = new File(fsName + ".tmp");
        
        // Create new empty filesystem
        mkfs(tempFile.getPath());
        
        // Re-add all active files (preserving their creation timestamps)
        try (RandomAccessFile raf = new RandomAccessFile(tempFile, "rw")) {
            // Update header to match our re-added files
            Header header = new Header();
            header.fileCount = (short) activeFiles.size();
            header.flags = (byte) (activeFiles.size() >= FILE_CAPACITY ? 1 : 0);
            header.deletedFiles = 0;
            
            // Write initial header
            raf.seek(0);
            raf.write(header.pack());
            
            // Track where we're writing data
            int currentDataOffset = DATA_START;
            int currentEntryOffset = HEADER_SIZE;
            
            // Re-add each active file
            for (FileData fileData : activeFiles) {
                // Calculate 64-byte aligned position
                int alignedStart = ((currentDataOffset + 63) / 64) * 64;
                int paddedLength = ((fileData.data.length + 63) / 64) * 64;
                
                // Write file data
                raf.seek(alignedStart);
                raf.write(fileData.data);
                if (paddedLength > fileData.data.length) {
                    raf.write(new byte[paddedLength - fileData.data.length]);
                }
                
                // Create and write file entry
                FileEntry entry = new FileEntry(
                    fileData.name,
                    alignedStart,
                    fileData.data.length,
                    (byte) 0,
                    fileData.created
                );
                
                raf.seek(currentEntryOffset);
                raf.write(entry.pack());
                
                // Update offsets
                currentDataOffset = alignedStart + paddedLength;
                currentEntryOffset += ENTRY_SIZE;
            }
            
            // Update final header values
            header.nextFreeOffset = currentDataOffset;
            header.freeEntryOffset = (currentEntryOffset < DATA_START) ? currentEntryOffset : 0;
            
            raf.seek(0);
            raf.write(header.pack());
        }

        // Replace old file with new defragmented file
        Files.delete(fsFile.toPath());
        Files.move(tempFile.toPath(), fsFile.toPath());

        System.out.println("Defragmentation complete!");
        System.out.println("Files removed: " + deletedCount);
        System.out.println("Bytes freed: " + bytesFreed);
        System.out.println("Active files after defragmentation: " + activeFiles.size());
    }

    // Helper class for dfrgfs
    static class FileData {
        String name;
        byte[] data;
        long created;
        
        FileData(String name, byte[] data, long created) {
            this.name = name;
            this.data = data;
            this.created = created;
        }
    }



    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Usage: java zvfs <command> <filesystem> [args...]");
            System.exit(1);
        }

        String command = args[0];
        String fsName = args[1];

        try {
            switch (command) {
                case "mkfs": mkfs(fsName); break;
                case "gifs": gifs(fsName); break;
                case "addfs":
                    if (args.length < 3) { System.out.println("Usage: java zvfs addfs <filesystem> <file_to_add>"); return; }
                    addfs(fsName, args[2]); break;
                case "getfs":
                    if (args.length < 3) { System.out.println("Usage: java zvfs getfs <filesystem> <file_to_extract>"); return; }
                    getfs(fsName, args[2]); break;
                case "rmfs":
                    if (args.length < 3) { System.out.println("Usage: java zvfs rmfs <filesystem> <file_to_remove>"); return; }
                    rmfs(fsName, args[2]); break;
                case "lsfs": lsfs(fsName); break;
                case "catfs":
                    if (args.length < 3) { System.out.println("Usage: java zvfs catfs <filesystem> <file_to_print>"); return; }
                    catfs(fsName, args[2]); break;
                case "dfrgfs": dfrgfs(fsName); break;
                default: System.out.println("Unknown command: " + command);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

}
