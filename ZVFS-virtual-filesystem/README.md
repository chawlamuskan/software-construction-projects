# HS25_SoCo-group_020-a3

**By:**  
**Dhani Arora – 24-730-590**  
**Muskan Chawla – 24-730-509**  
**Noémie Hungerbühler – 23-927-684**

---

# .zvfs Virtual Filesystem Project

## Overview

This project implements a simple virtual filesystem with the `.zvfs` format in Python.  
The filesystem allows users to perform common filesystem operations such as creating, adding, listing, reading, deleting, and defragmenting files.  

--- 

## File Descriptions

- `README.md` – Explains the project, decisions made, and documents usage of AI if any  
- `repository.md` – Stores the GitLab repository link for your group  
- `zvfs.py` – Python implementation of `.zvfs` filesystem commands  
- `zvfs.java` – Java implementation for the second part of the assignment  
- `zvfs.class` – Compiled Java bytecode of `zvfs.java`  
- `filesystem1.zvfs` – Sample filesystem created in Step 1  
- `filesystem2.zvfs` – Sample filesystem created in Step 2  

---

## Implemented Commands

1. `mkfs` – Create a new `.zvfs` filesystem  
   - Initializes the header with magic number, maximum entries, and total capacity  
   - Sets all file entries as empty and ready for use  

2. `addfs` – Add a file to the filesystem  
   - Checks for free entries  
   - Writes metadata (name, size, offset) to the entry table  
   - Appends file contents to the data section  
   - Uses Python `struct` to pack data into fixed-size binary blocks  

3. `lsfs` – List all files in the filesystem  
   - Reads the entry table  
   - Ignores entries marked as deleted  
   - Displays filenames and their sizes  

4. `catfs` – Display the contents of a file  
   - Reads the file’s offset and size from the entry table  
   - Outputs file content to console  

5. `getfs` – Extract a file to the host system  
   - Copies file data from the `.zvfs` file using the offset  
   - Writes it to a new file on the host filesystem  

6. `gifs` – Display filesystem information  
   - Shows total number of entries, free entries, deleted files, and used capacity  

7. `rmfs` – Remove a file from the filesystem  
   - Marks the corresponding entry as deleted  
   - Data remains in the file until `dfrgfs` is called  

8. `dfrgfs` – Defragment the filesystem  
   - Reclaims space from deleted files  
   - Compacts data so entries point to contiguous data blocks  

---

## Step 01: Demonstrating `.zvfs` Filesystem Management in Python

1. Creat a new filesystem `filesystem1.zvfs`
```bash
python zvfs.py mkfs filesystem1.zvfs 

Output in terminal: 
Created empty filesystem: filesystem1.zvfs 
```
Created a new file called `filesystem1.zvfs` in our folder with a fresh header 

2. Creat two text files
```bash
echo Hello, world! > test_file1.txt
echo The weather is nice today > test_file2.txt
```
Created a new file called `test_file1.txt` in our folder with the content "Hello, world!".
Created another filed called `test_file2.txt` in our folder with the content "The weather is nice today"
Both created on the host system 

3. Add both files to the filesystem
```bash 
python zvfs.py addfs filesystem1.zvfs test_file1.txt
python zvfs.py addfs filesystem1.zvfs test_file2.txt

Output in terminal: 
Added file: test_file1.txt (14 bytes), information on that file is at entry 64, the data is located at offset 2112 
Added file: test_file2.txt (26 bytes), information on that file is at entry 128, the data is located at offset 2176
```
Added both files to the filesystem in the next free entry and its data is written to the next 64-byte aligned offset.

4. List all filesystem files 
``` bash
python zvfs.py lsfs filesystem1.zvfs

Output in terminal: 
Files in virtual filesystem: filesystem1.zvfs
============================================================
Filename             Size (bytes) Created On          
------------------------------------------------------------
test_file1.txt       14           2025-12-05 15:37:36 
test_file2.txt       26           2025-12-05 15:39:38 
------------------------------------------------------------
Total files listed: 2
Filesystem capacity: 32 slots
Free slots remaining: 30
```
Listed all the files from our filesystem, only active (non - deleted) files 

5. Print contents of `test_file1.txt` from the filesystem
```bash 
python zvfs.py catfs filesystem1.zvfs test_file1.txt

Output in terminal: 
Contents of 'test_file1.txt':

Hello, world!
```
The data is read from the filesystem, and the contents are printed to the terminal exactly as stored

6. Delete file `test_file1.txt` from your disk, and restore it from the filesystem:
```bash
rm test_file1.txt
python zvfs.py getfs filesystem1.zvfs test_file1.txt

Output in terminal:
Extracted file: test_file1.txt (14 bytes) from filesystem1.zvfs
```
After the first command, the `test_file1.txt` is removed locally from the disk, but after the second command, the `test_file1.txt` is extracted from the filesystem and is visible again in the folder on the disk with its content. The getfs function extracts the stored copy from .zvfs and rewrites it back to the host disk with its original contents.

7. Get the information of the filesystem:
```bash
python zvfs.py gifs filesystem1.zvfs

Output in terminal:
Filesystem: filesystem1.zvfs
Files present: 2
Free entries: 30
Deleted files: 0
Total space used: 40 bytes
```
Prints a summary of the filesystem internals

8. Delete `test_file1.txt` from the filesystem, and then get the information of the filesystem and list all
filesystem files:
```bash
python zvfs.py rmfs filesystem1.zvfs test_file1.txt
python zvfs.py gifs filesystem1.zvfs
python zvfs.py lsfs filesystem1.zvfs

Output in terminal:
Removed test_file1.txt from filesystem. # after rmfs
Filesystem: filesystem1.zvfs            # after gifs
Files present: 1
Free entries: 30
Deleted files: 1
Total space used: 40 bytes
Files in virtual filesystem: filesystem1.zvfs   # after lsfs
============================================================
Filename             Size (bytes) Created On          
------------------------------------------------------------
test_file2.txt       26           2025-12-05 15:39:38 
------------------------------------------------------------
Total files listed: 1
Filesystem capacity: 32 slots
Free slots remaining: 30
```
rmfs sets the file entry’s deletion flag.
After that, gifs and lsfs update correctly:
- the file is no longer listed
- deleted file count increases
- only one active file remains

9. Defragment the filesystem, and then get the information of the filesystem and list all filesystem files
```bash 
python zvfs.py dfrgfs filesystem1.zvfs
python zvfs.py gifs filesystem1.zvfs
python zvfs.py lsfs filesystem1.zvfs

Output in terminal:
Found 1 file(s) marked for deletion    # start output from dfrgfs
Found 1 active file(s)
Defragmentation complete!
Files removed: 1
Bytes freed (file data not counting padding): 14
Active files after defragmentation: 1
Next free data offset: 2176            # end output from dfrgfs
Filesystem: filesystem1.zvfs           # start output from gifs
Files present: 1
Free entries: 31
Deleted files: 0
Total space used: 26 bytes             # end output from gifs
Files in virtual filesystem: filesystem1.zvfs      # start output from lsfs 
============================================================
Filename             Size (bytes) Created On          
------------------------------------------------------------
test_file2.txt       26           2025-12-05 15:39:38 
------------------------------------------------------------
Total files listed: 1
Filesystem capacity: 32 slots
Free slots remaining: 31                           # start output from lsfs 
```
The filesystem removes deleted entries permanently:
- marked as deleted files are fully removed
- active files are moved up in the filesystem so there is no empty slot left between 2 active files
- free entry count increases
- next free data offset is updated
- After defragmentation, only the remaining active file (`test_file2.txt`) is kept

---

## Step 02: Demonstrating `.zvfs` Filesystem Management in Java

### Challenges faced during python -> java translation

1. Packing / Unpacking Bytes 
   - In Python, `struct.pack` and `struct.unpack` make it easy to store and read structured data 
   - In Java, we have to do it manually using `ByteBuffer`. This means:  
     - Creating a buffer of the correct size  
     - Setting the byte order (little-endian in our case)
     - Adding or reading each field one by one using the right type (`putInt`, `putShort`, `put`, etc.) 
   - It’s easy to mess up the order or type, which can break the filesystem

2. File I/O Differences  
   - In Python, reading or writing bytes is simple with `open(file, "rb")` or `open(file, "wb")`
   - In Java, we need `RandomAccessFile` to read/write bytes at specific positions. We also have to `seek()` to the right spot before reading/writing  
   - Closing files is more strict in Java. We usually use `try-with-resources` to make sure files are closed automatically. (Safer than try() ... finally(close))

3. Exceptions 
   - Python uses `try/except` freely and it’s easy to catch errors 
   - In Java, file operations throw `IOException` and you must handle it with `try/catch` or add `throws IOException` to the method 

4. Byte Alignment / Padding
   - Python sometimes handles padding automatically with `struct`
   - In Java, we must calculate it manually, for example making sure each file starts at a multiple of 64 bytes  
   - Forgetting this can make the filesystem unreadable

5. Flags and Deletion Handling 
   - In Python, you can just write `flag = 1` and check `if flag:`
   - In Java, flags are bytes or integers, and you must check equality explicitly like `if (flag == 1)`
   - Easy to forget and caused bugs in the beginning 

6. Verbose Syntax and Object Handling
   - Java is more wordy than Python. You have to write semicolons, braces, types, and `new` for objects
   - It also uses {}, one first has to understand how to write java code and how to structure it. For example understand that we write: `public static main`, `ObjType name = new ObjType(params)`, `System.out.println()` etc.
   - Example:  
     ```java
     Header header = new Header();
     ```  
     vs Python:  
     ```python
     header = Header()
     ```

7. Working with `ByteBuffer`
   - `ByteBuffer` is used to pack/unpack binary data  
   - You need to remember:  
     - Set the byte order (`ByteOrder.LITTLE_ENDIAN`)
     - Use the correct `put`/`get` methods for each type (`putInt`, `getLong`, etc.)
     - Convert byte arrays to strings carefully, trimming extra zeros/padding

8. Always forgetting the semicolon at the end
   - It’s super easy to forget `;` at the end of a line. It happens again and again

--- 

## Step 02: Demonstrating `.zvfs` Filesystem Management in Java

Note: before starting the steps, run 
```bash
javac Header.java FileEntry.java zvfs.java
```
in the terminal.

1. Creat a new filesystem `filesystem2.zvfs`
```bash
java zvfs mkfs filesystem2.zvfs 

Output in terminal: 
Created empty filesystem: filesystem2.zvfs
```
Created a new file called `filesystem2.zvfs` in our folder with a fresh header 

2. Creat two text files
```bash
echo Hello, world! > test_file1.txt
echo The weather is nice today > test_file2.txt
```
Created a new file called `test_file1.txt` in our folder with the content "Hello, world!".
Created another filed called `test_file2.txt` in our folder with the content "The weather is nice today"
Both created on the host system 

3. Add both files to the filesystem
```bash 
java zvfs addfs filesystem2.zvfs test_file1.txt
java zvfs addfs filesystem2.zvfs test_file2.txt

Output in terminal: 
Added file: test_file1.txt (14 bytes)
Entry at 64, data at offset 2112
Added file: test_file2.txt (26 bytes)
Entry at 128, data at offset 2176
```
Added both files to the filesystem in the next free entry and its data is written to the next 64-byte aligned offset.

4. List all filesystem files 
``` bash
java zvfs lsfs filesystem2.zvfs

Output in terminal: 
Files in virtual filesystem: filesystem2.zvfs
============================================================
Filename             Size (bytes) Created On          
------------------------------------------------------------
test_file1.txt       14           2025-12-07 15:56:32 
test_file2.txt       26           2025-12-07 15:57:24 
------------------------------------------------------------
Total files listed: 2
Filesystem capacity: 32 slots
Free slots remaining: 30
```
Listed all the files from our filesystem, only active (non - deleted) files 

5. Print contents of `test_file1.txt` from the filesystem
```bash 
java zvfs catfs filesystem2.zvfs test_file1.txt

Output in terminal: 
Contents of 'test_file1.txt':
============================================================
Hello, world!

============================================================
```
The data is read from the filesystem, and the contents are printed to the terminal exactly as stored

6. Delete file `test_file1.txt` from your disk, and restore it from the filesystem:
```bash
rm test_file1.txt
java zvfs getfs filesystem2.zvfs test_file1.txt

Output in terminal:
Extracted file: test_file1.txt (14 bytes) from filesystem2.zvfs
```
After the first command, the `test_file1.txt` is removed locally from the disk, but after the second command, the `test_file1.txt` is extracted from the filesystem and is visible again in the folder on the disk with its content. The getfs function extracts the stored copy from .zvfs and rewrites it back to the host disk with its original contents.

7. Get the information of the filesystem:
```bash
java zvfs gifs filesystem2.zvfs

Output in terminal:
Filesystem: filesystem2.zvfs
Files present: 2
Free entries: 30
Deleted files: 0
Total space used: 40 bytes
```
Prints a summary of the filesystem internals

8. Delete `test_file1.txt` from the filesystem, and then get the information of the filesystem and list all
filesystem files:
```bash
java zvfs rmfs filesystem2.zvfs test_file1.txt
java zvfs gifs filesystem2.zvfs
java zvfs lsfs filesystem2.zvfs

Output in terminal:
Removed file: test_file1.txt from filesystem.      # after rmfs
Filesystem: filesystem2.zvfs        # after gifs
Files present: 2
Free entries: 30
Deleted files: 1
Total space used: 40 bytes
Files in virtual filesystem: filesystem2.zvfs      # after lsfs
============================================================
Filename             Size (bytes) Created On          
------------------------------------------------------------
test_file2.txt       26           2025-12-07 15:57:24 
------------------------------------------------------------
Total files listed: 1
Filesystem capacity: 32 slots
Free slots remaining: 30
```
rmfs sets the file entry’s deletion flag.
After that, gifs and lsfs update correctly:
- the file is no longer listed
- deleted file count increases
- only one active file remains

9. Defragment the filesystem, and then get the information of the filesystem and list all filesystem files
```bash 
java zvfs dfrgfs filesystem2.zvfs
java zvfs gifs filesystem2.zvfs
java zvfs lsfs filesystem2.zvfs

Output in terminal:
Found 1 file(s) marked for deletion       # start dfrgfs
Found 1 active file(s) to keep
Created empty filesystem: filesystem2.zvfs.tmp
Defragmentation complete!
Files removed: 1
Bytes freed: 14
Active files after defragmentation: 1        # end dfrgfs
Filesystem: filesystem2.zvfs           # start gifs
Files present: 1
Free entries: 31
Deleted files: 0
Total space used: 26 bytes          # end gifs
Files in virtual filesystem: filesystem2.zvfs      # start lsfs
============================================================
Filename             Size (bytes) Created On          
------------------------------------------------------------
test_file2.txt       26           2025-12-07 15:57:24 
------------------------------------------------------------
Total files listed: 1
Filesystem capacity: 32 slots
Free slots remaining: 31         # end lsfs
```
The filesystem removes deleted entries permanently:
- marked as deleted files are fully removed
- active files are moved up in the filesystem so there is no empty slot left between 2 active files
- free entry count increases
- next free data offset is updated
- After defragmentation, only the remaining active file (`test_file2.txt`) is kept

---

## Check Python <-> Java 

Goal:
- Java can read the filesystem created by Python (filesystem1.zvfs)
- Python can read the filesystem created by Java (filesystem2.zvfs)

---

### Java reading Python `filesystem1.zvfs`

1. List files using java 
```bash
java zvfs lsfs filesystem1.zvfs

Output in terminal:
Files in virtual filesystem: filesystem1.zvfs
============================================================
Filename             Size (bytes) Created On          
------------------------------------------------------------
test_file2.txt       26           2025-12-05 16:20:56 
------------------------------------------------------------
Total files listed: 1
Filesystem capacity: 32 slots
Free slots remaining: 31
```

2. Try printing a file using `catfs`in Java
```bash
java zvfs catfs filesystem1.zvfs test_file1.txt

Output in terminal:
Error: File 'test_file1.txt' not found in filesystem.
```
Because it does not exist in the filesystem

**But**
```bash
java zvfs catfs filesystem1.zvfs test_file2.txt

Output in terminal:
Contents of 'test_file2.txt':
============================================================
The weather is nice today

============================================================
```
exists. 

3. Try `gifs`using Java 
```bash
java zvfs gifs filesystem1.zvfs 

Output in Terminal:
Filesystem: filesystem1.zvfs
Files present: 1
Free entries: 31
Deleted files: 0
Total space used: 26 bytes
```

--- 

### Python reading Java `filesystem2.zvfs`

1. List files using python 
```bash
python zvfs.py lsfs filesystem2.zvfs

Output in terminal:
Files in virtual filesystem: filesystem2.zvfs
============================================================
Filename             Size (bytes) Created On          
------------------------------------------------------------
test_file2.txt       26           2025-12-07 15:57:24 
------------------------------------------------------------
Total files listed: 1
Filesystem capacity: 32 slots
Free slots remaining: 31
```

2. Try printing a file using `catfs`in python
```bash
python zvfs.py catfs filesystem2.zvfs test_file1.txt

Output in terminal:
Error: File 'test_file1.txt' not found in filesystem.
```
Because it does not exist in the filesystem

**But**

```bash
python zvfs.py catfs filesystem2.zvfs test_file2.txt

Output in terminal:
Contents of 'test_file2.txt':

The weather is nice today
```
exists. 

3. Try `gifs`using Java 
```bash
python zvfs.py gifs filesystem2.zvfs 

Output in Terminal:
Filesystem: filesystem2.zvfs
Files present: 1
Free entries: 31
Deleted files: 0
Total space used: 26 bytes
```
4. Create a test_file3.txt and add it using the java implementation `addfs` to filesystem1.zvfs and then list all the files using the python implementation `lsfs` to see if the file appears in the python created filesystem1.zvfs. Make sure the file contains the right content by calling the python implementation of `catfs`.

```bash
echo this file will be added to filesystem1.zvfs using the java implementation of addfs > test_file3.txt
java zvfs addfs filesystem1.zvfs test_file3.txt
python zvfs.py lsfs filesystem1.zvfs 
python zvfs.py catfs filesystem1.zvfs test_file3.txt

Output in Terminal:
Added file: test_file3.txt (83 bytes)           # after java addfs
Entry at 128, data at offset 2176
Files in virtual filesystem: filesystem1.zvfs   # after py lsfs
============================================================
Filename             Size (bytes) Created On          
------------------------------------------------------------
test_file2.txt       26           2025-12-05 16:20:56 
test_file3.txt       83           2025-12-07 16:55:44 
------------------------------------------------------------
Total files listed: 2
Filesystem capacity: 32 slots
Free slots remaining: 30
Contents of 'test_file3.txt':                   # after py catfs

this file will be added to filesystem1.zvfs using the java implementation of addfs
```

---

### Use of AI:

Prompt: i have a header format: HEADER_FORMAT = "8s B B h h h h h i i i i h 26s" and a file entry format: FILE_ENTRY_FORMAT = "32s i i B B h d 12s". I keep getting the error message : "struct.error: unpack requires a buffer of 68 bytes" but i don't understand what it means. Explain what this error means and give me a hint on how I could correct it 

Prompt: i want to make the output of one of my functions look more structured, is there a simple way to print my output in a table with 3 different columns (title of each column at the top and for each object populate one line)? 

Prompt: i want to make the output of one of my functions look more structured, is there a simple way to print my output in a table with 3 different columns (title of each column at the top and for each object populate one line) but for java? 