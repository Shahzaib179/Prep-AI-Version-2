from dataclasses import dataclass
import io,json,re,streamlit as st
SUPPORTED={".pdf",".docx",".txt",".md"}
@dataclass
class DriveFile:
    name:str
    content:bytes
class GoogleDriveSource:
    def __init__(self):
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError as e: raise RuntimeError("Install requirements.txt for Google Drive support.") from e
        raw=st.secrets.get("GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON")
        if not raw: raise RuntimeError("Add GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON to Streamlit Secrets.")
        info=json.loads(raw) if isinstance(raw,str) else dict(raw)
        cred=service_account.Credentials.from_service_account_info(info,scopes=["https://www.googleapis.com/auth/drive.readonly"])
        self.client=build("drive","v3",credentials=cred,cache_discovery=False)
    def ids(self,url):
        f=re.search(r"/file/d/([\w-]+)",url); d=re.search(r"/folders/([\w-]+)",url)
        q=re.search(r"[?&]id=([\w-]+)",url)
        return (f.group(1) if f else (q.group(1) if q and "/folders/" not in url else None)),(d.group(1) if d else None)
    def download(self,fid,name):
        from googleapiclient.http import MediaIoBaseDownload
        buf=io.BytesIO(); dl=MediaIoBaseDownload(buf,self.client.files().get_media(fileId=fid)); done=False
        while not done: _,done=dl.next_chunk()
        return DriveFile(name,buf.getvalue())
    def load(self,url):
        fid,folder=self.ids(url); out=[]
        if folder:
            token=None
            while True:
                r=self.client.files().list(q=f"'{folder}' in parents and trashed=false",fields="nextPageToken,files(id,name,mimeType)",pageToken=token,pageSize=100).execute()
                for x in r.get("files",[]):
                    if any(x["name"].lower().endswith(e) for e in SUPPORTED): out.append(self.download(x["id"],x["name"]))
                token=r.get("nextPageToken")
                if not token: break
            return out
        if fid:
            m=self.client.files().get(fileId=fid,fields="id,name").execute()
            return [self.download(fid,m["name"])] if any(m["name"].lower().endswith(e) for e in SUPPORTED) else []
        raise ValueError("Unsupported Google Drive URL.")
