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
        // portable-pty calls setsid before exec. The practice bash disables monitor
        // mode, so normal foreground/background commands inherit this owned group.
        if unsafe{libc::getpgid(pid)}!=pid{return Err("실습 프로세스 그룹을 확인하지 못했어요.".into())}
        Ok(Self(pid))
    }
    pub fn terminate(&self)->Result<(),String> {
        if unsafe{libc::kill(-self.0,libc::SIGKILL)}==0{return Ok(())}
        let error=std::io::Error::last_os_error();if error.raw_os_error()==Some(libc::ESRCH){Ok(())}else{Err(error.to_string())}
    }
}
