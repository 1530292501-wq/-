"""Local-only Iwakura Aria Chinese text patch installer. Python standard library."""
from pathlib import Path
import base64, gzip, hashlib, json, os, shutil, struct, subprocess, sys, zlib

def sha(b): return hashlib.sha256(b).hexdigest()

def archive_entries(b):
    if b[:8] != b'MPK\0\0\0\2\0': raise ValueError('不支持的资源格式。')
    n=struct.unpack_from('<I',b,8)[0]
    entries=[]
    for i in range(n):
        flags,idx,off,size,usize=struct.unpack_from('<IIQQQ',b,64+i*256)
        name=b[96+i*256:320+i*256].split(b'\0')[0].decode('ascii')
        if flags or size!=usize or off+size>len(b): raise ValueError('资源条目异常。')
        entries.append((name,b[off:off+size]))
    return entries

def repack(b, replacements):
    entries=archive_entries(b)
    if not set(replacements)<=dict(entries).keys(): raise ValueError('资源缺少必要条目。')
    out=bytearray(b[:64+256*len(entries)])
    out.extend(bytes((-len(out))%2048))
    for i,(name,old) in enumerate(entries):
        data=replacements.get(name,old)
        struct.pack_into('<QQQ',out,72+i*256,len(out),len(data),len(data))
        out.extend(data)
        if i+1<len(entries):out.extend(bytes((-len(out))%2048))
    result=bytes(out)
    assert dict(archive_entries(result))=={n:replacements.get(n,d) for n,d in entries}
    return result

def png_chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)

def append_font_rows(png, rows, extra_height):
    if png[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('字库图片格式异常。')
    chunks=[];pos=8
    while pos<len(png):
        size=struct.unpack_from('>I',png,pos)[0];kind=png[pos+4:pos+8];data=png[pos+8:pos+8+size]
        if zlib.crc32(kind+data)&0xffffffff!=struct.unpack_from('>I',png,pos+8+size)[0]:raise ValueError('字库图片校验失败。')
        chunks.append((kind,data));pos+=12+size
    ihdr=next(d for k,d in chunks if k==b'IHDR')
    w,h,depth,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',ihdr)
    if (w,h,depth,color,compression,filtering,interlace)!=(4096,6694,8,0,0,0,0):raise ValueError('不支持此版本字库。')
    scanlines=zlib.decompress(b''.join(d for k,d in chunks if k==b'IDAT'))
    assert len(scanlines)==h*(w+1) and len(rows)==w*extra_height
    # Keep original filtered scanlines verbatim. New rows use filter type zero.
    appended=b''.join(b'\0'+rows[y*w:(y+1)*w] for y in range(extra_height))
    new_header=struct.pack('>IIBBBBB',w,h+extra_height,depth,color,compression,filtering,interlace)
    ancillary=b''.join(png_chunk(k,d) for k,d in chunks if k not in (b'IHDR',b'IDAT',b'IEND'))
    return png[:8]+png_chunk(b'IHDR',new_header)+ancillary+png_chunk(b'IDAT',zlib.compress(scanlines+appended,9))+png_chunk(b'IEND',b'')

def synthesize(originals,payload):
    scripts={n:base64.b64decode(v) for n,v in payload['scripts'].items()}
    system=dict(archive_entries(originals['system_jpn_win.mpk']))
    font=append_font_rows(system['font_df_jpn.png'],zlib.decompress(base64.b64decode(payload['font_rows'])),payload['extra_height'])
    metrics=bytearray(system['font_df_jpn.bin'])
    for idx,data in payload['metrics']:
        replacement=bytes.fromhex(data)
        assert len(replacement)==16 and 0<=idx<7424
        metrics[idx*16:idx*16+16]=replacement
    replacements={'mes00.mpk':scripts,'system_jpn_win.mpk':{'font_df_jpn.png':font,'font_df_jpn.bin':bytes(metrics)}}
    if payload.get('ui_rectangles'):
        from png_rect_patch import patch_rgba_png
        groups={}
        for patch in payload['ui_rectangles']:groups.setdefault((patch['archive'],patch['file']),[]).append(patch)
        for (archive,name),patches in groups.items():
            original=dict(archive_entries(originals[archive]))[name]
            replacements.setdefault(archive,{})[name]=patch_rgba_png(original,patches)
    return {n:repack(originals[n],r) for n,r in replacements.items()}

def main():
    root=Path(sys.executable if getattr(sys,'frozen',False) else __file__).resolve().parent
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    undo='--restore' in sys.argv
    paths=[a for a in sys.argv[1:] if not a.startswith('--')]
    game=Path(paths[0] if paths else input('请输入游戏文件夹路径（不要加引号）：\n').strip().strip('"')).resolve()
    if not (game/'Data').is_dir():raise ValueError('没有找到游戏 Data 文件夹。')
    if os.name=='nt':
        shell=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
        probe=subprocess.run([str(shell),'-NoProfile','-NonInteractive','-Command',
            "try { if (@(Get-Process -ErrorAction Stop | Where-Object { $_.ProcessName -ieq 'IWAKURA_ARIA' }).Count -gt 0) { exit 2 }; exit 0 } catch { exit 1 }"],
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=0x08000000,timeout=30)
        if probe.returncode==2:raise ValueError('请先关闭游戏，再安装或还原。')
        if probe.returncode!=0:raise ValueError('无法确认游戏是否关闭，未作修改。请关闭游戏后重试。')
    backup=game/'IwakuraAria_CN_Backup'
    names=list(manifest['source_archives'])
    current={n:(game/'Data'/n).read_bytes() for n in names}
    if undo:
        for n in names:
            original=backup/n
            if not original.is_file() or sha(original.read_bytes())!=manifest['source_archives'][n]:raise ValueError('原版备份缺失或校验失败，未作修改。')
            accepted={manifest['target_archives'][n],manifest['source_archives'][n]}
            accepted.update(p[n] for p in manifest.get('previous_targets',[]) if n in p)
            if sha(current[n]) not in accepted:raise ValueError('游戏文件已被其他更新修改，为避免覆盖，停止还原。')
        for n in names:
            shutil.copy2(backup/n,game/'Data'/n)
            assert sha((game/'Data'/n).read_bytes())==manifest['source_archives'][n]
        print('已还原原版资源。备份保留，存档未作改动。');return
    if all(sha(current[n])==manifest['target_archives'][n] for n in names):
        print('此版本汉化已安装。请在游戏中使用日语／简体中文语言槽。');return
    current_hashes={n:sha(b) for n,b in current.items()}
    upgrading=current_hashes in manifest.get('previous_targets',[])
    originals=dict(current)
    if upgrading:
        for n in names:
            if current_hashes[n]!=manifest['source_archives'][n]:
                saved=backup/n
                if not saved.is_file() or sha(saved.read_bytes())!=manifest['source_archives'][n]:raise ValueError('升级所需的原版备份缺失或校验失败，未作修改。')
                originals[n]=saved.read_bytes()
    for n in names:
        if sha(originals[n])!=manifest['source_archives'][n]:raise ValueError('游戏版本不匹配，或已有其他补丁：'+n+'。未作修改。')
    packed=(root/'payload.json.gz').read_bytes()
    if sha(packed)!=manifest['payload_sha256']:raise ValueError('补丁包校验失败，请重新解压。')
    built=synthesize(originals,json.loads(gzip.decompress(packed)))
    for n,data in built.items():
        if sha(data)!=manifest['target_archives'][n]:raise ValueError('合成结果校验失败，未作修改：'+n)
    backup.mkdir(exist_ok=True)
    for n in names:
        p=backup/n
        if p.exists() and sha(p.read_bytes())!=manifest['source_archives'][n]:raise ValueError('已有不匹配的备份，未作修改。')
    for n in names:
        if not (backup/n).exists():(backup/n).write_bytes(originals[n])
    staged=[]
    try:
        for n,data in built.items():
            p=game/'Data'/(n+'.cn-stage');p.write_bytes(data);staged.append(p)
            assert sha(p.read_bytes())==manifest['target_archives'][n]
        for n,p in zip(names,staged):os.replace(p,game/'Data'/n)
        for n in names:assert sha((game/'Data'/n).read_bytes())==manifest['target_archives'][n]
    except BaseException:
        for n in names:(game/'Data'/n).write_bytes(current[n])
        raise
    finally:
        for p in staged:
            if p.exists():p.unlink()
    (backup/'installation.json').write_text(json.dumps({'version':manifest['version'],'target_archives':manifest['target_archives']},indent=2),encoding='utf-8')
    print('汉化安装完成。请使用游戏的日语／简体中文语言槽。存档未作改动。')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('操作停止：'+str(exc));sys.exit(1)
