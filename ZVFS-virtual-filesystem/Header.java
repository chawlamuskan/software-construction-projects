import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class Header {

    // ==== CONSTANTS ====
    static final int HEADER_SIZE = 64;
    static final int FILE_CAPACITY = 32;
    static final int ENTRY_SIZE = 64;
    static final int DATA_START = HEADER_SIZE + FILE_CAPACITY * ENTRY_SIZE;   // 64 + 2048 = 2112
    static final long MAX_OFFSET = (1L << 32);
    static final byte[] MAGIC = "ZVFSDSK1".getBytes();   // 8 bytes
    static final int VERSION = 1;

    public byte[] magic = MAGIC;     // 8 bytes
    public byte version = (byte) VERSION;
    public byte flags;               // 0 = free entry available, 1 = full
    public short reserved0 = 0;

    public short fileCount = 0;                  // active entries
    public short fileCapacity = (short) FILE_CAPACITY;
    public short fileEntrySize = (short) ENTRY_SIZE;
    public short reserved1 = 0;

    public int fileTableOffset = HEADER_SIZE;    // 64
    public int dataStartOffset = DATA_START;     // 2112

    public int nextFreeOffset = DATA_START;      // where next file data goes
    public int freeEntryOffset = HEADER_SIZE;    // where next entry goes

    public short deletedFiles = 0;
    public byte[] reserved2 = new byte[26];      // 26 zero bytes

    public Header() {}   // constructor for a default filesystem header

    // pack fields to 64 bytes exactly (HEADER_FMT)
    public byte[] pack() {
        ByteBuffer buf = ByteBuffer.allocate(HEADER_SIZE);
        buf.order(ByteOrder.LITTLE_ENDIAN);

        buf.put(magic);                  // 8s
        buf.put(version);                // B
        buf.put(flags);                  // B
        buf.putShort(reserved0);         // H
        buf.putShort(fileCount);         // H
        buf.putShort(fileCapacity);      // H
        buf.putShort(fileEntrySize);     // H
        buf.putShort(reserved1);         // H
        buf.putInt(fileTableOffset);     // I
        buf.putInt(dataStartOffset);     // I
        buf.putInt(nextFreeOffset);      // I
        buf.putInt(freeEntryOffset);     // I
        buf.putShort(deletedFiles);      // H
        buf.put(reserved2);              // 26s

        return buf.array();
    }

    public void unpack(byte[] data) {
        ByteBuffer buf = ByteBuffer.wrap(data);
        buf.order(ByteOrder.LITTLE_ENDIAN);

        magic = new byte[8];
        buf.get(magic);                 // 8s

        version = buf.get();            // B
        flags = buf.get();              // B
        reserved0 = buf.getShort();     // H

        fileCount = buf.getShort();     // H
        fileCapacity = buf.getShort();  // H
        fileEntrySize = buf.getShort(); // H
        reserved1 = buf.getShort();     // H

        fileTableOffset = buf.getInt(); // I
        dataStartOffset = buf.getInt(); // I
        nextFreeOffset = buf.getInt();  // I
        freeEntryOffset = buf.getInt(); // I

        deletedFiles = buf.getShort();  // H

        reserved2 = new byte[26];
        buf.get(reserved2);             // 26s
    }    
}

