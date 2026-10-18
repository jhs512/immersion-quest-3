//! Lifetime ownership for a practice shell and its inherited descendants.
#[cfg(windows)]
pub struct ProcessScope(windows_sys::Win32::Foundation::HANDLE);
#[cfg(windows)]
unsafe impl Send for ProcessScope {}
#[cfg(windows)]
impl ProcessScope {
    pub fn attach(child:&dyn portable_pty::Child)->Result<Self,String> {
        use windows_sys::Win32::System::JobObjects::*;
        let process=child.as_raw_handle().ok_or("터미널 프로세스 핸들이 없어요.")?;
        // A private unnamed job cannot accidentally select an unrelated process tree.
        let handle=unsafe{CreateJobObjectW(std::ptr::null(),std::ptr::null())};
        if handle.is_null(){return Err(std::io::Error::last_os_error().to_string())}
        let scope=Self(handle);let mut limits=JOBOBJECT_EXTENDED_LIMIT_INFORMATION::default();
        limits.BasicLimitInformation.LimitFlags=JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE;
        let configured=unsafe{SetInformationJobObject(handle,JobObjectExtendedLimitInformation,&limits as *const _ as *const _,std::mem::size_of_val(&limits) as u32)};
        if configured==0||unsafe{AssignProcessToJobObject(handle,process)}==0 {return Err(std::io::Error::last_os_error().to_string())}
        Ok(scope)
    }
    pub fn terminate(&self)->Result<(),String> {
        use windows_sys::Win32::System::JobObjects::*;
        if unsafe{TerminateJobObject(self.0,1)}==0{return Err(std::io::Error::last_os_error().to_string())}
        for _ in 0..50 {
            let mut info=JOBOBJECT_BASIC_ACCOUNTING_INFORMATION::default();
            if unsafe{QueryInformationJobObject(self.0,JobObjectBasicAccountingInformation,&mut info as *mut _ as *mut _,std::mem::size_of_val(&info) as u32,std::ptr::null_mut())}==0{return Err(std::io::Error::last_os_error().to_string())}
            if info.ActiveProcesses==0{return Ok(())}
            std::thread::sleep(std::time::Duration::from_millis(100));
        }
        Err("실습 프로세스가 아직 종료되지 않았어요.".into())
    }
}
#[cfg(windows)]
impl Drop for ProcessScope {fn drop(&mut self){unsafe{windows_sys::Win32::Foundation::CloseHandle(self.0);}}}
#[cfg(unix)]
pub struct ProcessScope(libc::pid_t);
#[cfg(unix)]
impl ProcessScope {
    pub fn attach(child:&dyn portable_pty::Child)->Result<Self,String> {
        let pid=child.process_id().ok_or("터미널 프로세스 ID가 없어요.")? as libc::pid_t;
        // portable-pty calls setsid before exec. Keep the session ID even when
        // an interactive shell creates separate foreground/background groups.
        if unsafe{libc::getsid(pid)}!=pid{return Err("실습 프로세스 그룹을 확인하지 못했어요.".into())}
        Ok(Self(pid))
    }
    pub fn terminate(&self)->Result<(),String> {
        // Interactive shells can put background jobs in another process group.
        // Session membership still identifies those inherited children. Recheck it
        // before each signal; unrelated processes are never selected by name.
        for _ in 0..50 {
            let output=std::process::Command::new("/bin/ps").args(["-axo","pid=,stat="]).output().map_err(|e|e.to_string())?;
            if !output.status.success(){return Err("실습 프로세스 목록을 확인하지 못했어요.".into())}
            let mut running=false;
            for line in String::from_utf8_lossy(&output.stdout).lines() {
                let mut fields=line.split_whitespace();
                let Some(pid)=fields.next().and_then(|pid|pid.parse::<libc::pid_t>().ok()) else{continue};
                if fields.next().is_some_and(|state|state.starts_with('Z')){continue;}
                if pid>1&&unsafe{libc::getsid(pid)}==self.0 {
                    running=true;
                    if unsafe{libc::kill(pid,libc::SIGKILL)}!=0 {
                        let error=std::io::Error::last_os_error();if error.raw_os_error()!=Some(libc::ESRCH){return Err(error.to_string())}
                    }
                }
            }
            if !running{return Ok(())}
            std::thread::sleep(std::time::Duration::from_millis(100));
        }
        Err("실습 프로세스가 아직 종료되지 않았어요.".into())
    }
}
