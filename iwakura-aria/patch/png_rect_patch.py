"""Lossless local PNG atlas edits, standard library only; payload contains new pixels only."""
import struct,zlib,base64

def chunk(k,d):return struct.pack('>I',len(d))+k+d+struct.pack('>I',zlib.crc32(k+d)&0xffffffff)

def patch_rgba_png(png,patches):
    assert png[:8]==b'\x89PNG\r\n\x1a\n'
    pos=8;chunks=[]
    while pos<len(png):
        n=struct.unpack_from('>I',png,pos)[0];k=png[pos+4:pos+8];d=png[pos+8:pos+8+n]
        assert zlib.crc32(k+d)&0xffffffff==struct.unpack_from('>I',png,pos+8+n)[0]
        chunks.append((k,d));pos+=n+12
        if k==b'IEND':break
    trailing_metadata=png[pos:]
    ihdr=next(d for k,d in chunks if k==b'IHDR')
    w,h,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',ihdr)
    assert (depth,color,compression,filtering,interlace)==(8,6,0,0,0)
    raw=zlib.decompress(b''.join(d for k,d in chunks if k==b'IDAT'))
    stride=w*4;assert len(raw)==h*(stride+1)
    rows=[];previous=bytearray(stride)
    for y in range(h):
        at=y*(stride+1);f=raw[at];row=bytearray(raw[at+1:at+1+stride])
        if f==1:
            for i in range(4,stride):row[i]=(row[i]+row[i-4])&255
        elif f==2:
            row=bytearray((a+b)&255 for a,b in zip(row,previous))
        elif f==3:
            for i in range(stride):row[i]=(row[i]+((row[i-4] if i>=4 else 0)+previous[i])//2)&255
        elif f==4:
            for i in range(stride):
                a=row[i-4] if i>=4 else 0;b=previous[i];c=previous[i-4] if i>=4 else 0
                p=a+b-c;pa=abs(p-a);pb=abs(p-b);pc=abs(p-c)
                prediction=a if pa<=pb and pa<=pc else b if pb<=pc else c
                row[i]=(row[i]+prediction)&255
        else:assert f==0
        rows.append(row);previous=row
    for patch in patches:
        x,y,r,b=patch['box'];assert 0<=x<r<=w and 0<=y<b<=h
        pixels=zlib.decompress(base64.b64decode(patch['rgba_zlib']));pw=(r-x)*4
        assert len(pixels)==pw*(b-y)
        for dy in range(b-y):rows[y+dy][x*4:r*4]=pixels[dy*pw:(dy+1)*pw]
    data=zlib.compress(b''.join(b'\0'+row for row in rows),9)
    ancillary=b''.join(chunk(k,d) for k,d in chunks if k not in (b'IHDR',b'IDAT',b'IEND'))
    return png[:8]+chunk(b'IHDR',ihdr)+ancillary+chunk(b'IDAT',data)+chunk(b'IEND',b'')+trailing_metadata
