//! Per-data-directory instance routing. The locked file survives process crashes
//! safely; localhost requests require a random token and never execute code.
use super::*;
use std::{fs::{File,OpenOptions},io::{BufRead,BufReader,Read,Write},net::{TcpListener,TcpStream},path::{Path,PathBuf},sync::{Arc,atomic::{AtomicBool,Ordering}},time::{Duration,Instant}};
#[derive(Serialize,Deserialize)]
struct Endpoint {port:u16,token:String}
#[derive(Serialize,Deserialize)]
struct Message {token:String,link:Option<String>}
pub struct Instance {_lock:File,stop:Arc<AtomicBool>,thread:Option<std::thread::JoinHandle<()>>,endpoint:PathBuf}
impl Instance {
    /// None means the existing player acknowledged the request.
    pub fn claim(directory:&Path,link:Option<&str>)->Result<Option<Self>,String>{
        std::fs::create_dir_all(directory).map_err(|e|e.to_string())?;
        let lock=OpenOptions::new().read(true).write(true).create(true).truncate(false).open(directory.join("player-instance.lock")).map_err(|e|e.to_string())?;
        let path=directory.join("player-instance.json");
        match lock.try_lock(){
            Ok(())=>{},
            Err(std::fs::TryLockError::WouldBlock)=>{Self::forward(&path,link)?;return Ok(None)},
            Err(error)=>return Err(error.to_string()),
        }
        let listener=TcpListener::bind((std::net::Ipv4Addr::LOCALHOST,0)).map_err(|e|e.to_string())?;
        listener.set_nonblocking(true).map_err(|e|e.to_string())?;
        let endpoint=Endpoint{port:listener.local_addr().map_err(|e|e.to_string())?.port(),token:crate::issue_progress::new_id()};
        std::fs::write(&path,serde_json::to_vec(&endpoint).unwrap()).map_err(|e|e.to_string())?;
        let stop=Arc::new(AtomicBool::new(false));let stopped=stop.clone();
        let worker=std::thread::spawn(move||{
            while !stopped.load(Ordering::Relaxed){
                match listener.accept(){
                    Ok((mut socket,_))=>{
                        let _=socket.set_read_timeout(Some(Duration::from_millis(500)));let _=socket.set_write_timeout(Some(Duration::from_millis(500)));
                        let mut raw=String::new();
                        if BufReader::new((&mut socket).take(4097)).read_line(&mut raw).is_ok()&&raw.len()<=4096 {
                            if let Ok(message)=serde_json::from_str::<Message>(&raw){if message.token==endpoint.token {
                                if let Some(link)=message.link {receive(&link)}else{put(Request::Focus)}
                                let _=socket.write_all(b"ok\n");
                            }}
                        }
                    },
                    Err(error) if error.kind()==std::io::ErrorKind::WouldBlock=>std::thread::sleep(Duration::from_millis(25)),
                    Err(_)=>break,
                }
            }
        });
        if let Some(link)=link{receive(link)}
        Ok(Some(Self{_lock:lock,stop,thread:Some(worker),endpoint:path}))
    }
    fn forward(path:&Path,link:Option<&str>)->Result<(),String>{
        let deadline=Instant::now()+Duration::from_secs(5);
        while Instant::now()<deadline {
            let attempt=||->Result<(),String>{
                if std::fs::metadata(path).map_err(|e|e.to_string())?.len()>4096{return Err("앱 연결 정보를 확인하세요.".into())}
                let endpoint:Endpoint=serde_json::from_slice(&std::fs::read(path).map_err(|e|e.to_string())?).map_err(|e|e.to_string())?;
                let mut socket=TcpStream::connect_timeout(&std::net::SocketAddr::from((std::net::Ipv4Addr::LOCALHOST,endpoint.port)),Duration::from_millis(300)).map_err(|e|e.to_string())?;
                socket.set_read_timeout(Some(Duration::from_millis(500))).map_err(|e|e.to_string())?;
                socket.set_write_timeout(Some(Duration::from_millis(500))).map_err(|e|e.to_string())?;
                writeln!(socket,"{}",serde_json::to_string(&Message{token:endpoint.token,link:link.map(str::to_owned)}).unwrap()).map_err(|e|e.to_string())?;
                let mut reply=String::new();BufReader::new(socket).read_line(&mut reply).map_err(|e|e.to_string())?;
                if reply=="ok\n"{Ok(())}else{Err("앱 응답을 확인하세요.".into())}
            };
            if attempt().is_ok(){return Ok(())}std::thread::sleep(Duration::from_millis(100));
        }
        Err("열려 있는 MQ에 연결하지 못했어요. MQ를 닫고 다시 여세요.".into())
    }
}
impl Drop for Instance {fn drop(&mut self){self.stop.store(true,Ordering::Relaxed);if let Some(worker)=self.thread.take(){let _=worker.join();}let _=std::fs::remove_file(&self.endpoint);}}
