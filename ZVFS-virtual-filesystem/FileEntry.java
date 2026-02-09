import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class FileEntry {

    static final int ENTRY_SIZE = 64;
    static final byte TYPE = 0;

    public String name = "";
    public int start = 0;
    public int length = 0;
    public byte type = TYPE;
    public byte flag = 0;        // 1 = deleted
    public short reserved0 = 0;
    public long created = 0;
    public byte[] reserved1 = new byte[12];

    public FileEntry() {}

    public FileEntry(String name, int start, int length, byte flag, long created) {
        if (start % 64 != 0)
            throw new IllegalArgumentException("start offset must be 64-byte aligned");

        this.name = name;
        this.start = start;
        this.length = length;
        this.flag = flag;
        this.created = created;
    }

    // pack entry into exactly 64 bytes
    public byte[] pack() {
        ByteBuffer buf = ByteBuffer.allocate(ENTRY_SIZE);
        buf.order(ByteOrder.LITTLE_ENDIAN);

        // encode name
        byte[] nameBytes = name.getBytes();
        if (nameBytes.length > 32)
            throw new IllegalArgumentException("File name too long (max 32 bytes)");

        byte[] paddedName = new byte[32];
        System.arraycopy(nameBytes, 0, paddedName, 0, nameBytes.length);
        buf.put(paddedName);

        buf.putInt(start);
        buf.putInt(length);
        buf.put(type);
        buf.put(flag);
        buf.putShort(reserved0);
        buf.putLong(created);
        buf.put(reserved1); // 12 bytes

        return buf.array();
    }

    // unpack 64 bytes into fields
    public FileEntry unpack(byte[] data) {
        ByteBuffer buf = ByteBuffer.wrap(data);
        buf.order(ByteOrder.LITTLE_ENDIAN);

        byte[] rawName = new byte[32];
        buf.get(rawName);

        // trim at null byte
        int end = 0;
        while (end < 32 && rawName[end] != 0) end++;
        this.name = new String(rawName, 0, end);

        this.start = buf.getInt();
        this.length = buf.getInt();
        this.type = buf.get();
        this.flag = buf.get();
        this.reserved0 = buf.getShort();
        this.created = buf.getLong();

        buf.get(this.reserved1);

        return this;
    }
}

