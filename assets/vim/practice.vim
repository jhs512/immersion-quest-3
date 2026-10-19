" Only this lesson's private HOME and files are used. No user vimrc is sourced.
set nocompatible noswapfile nobackup nowritebackup viminfo=
set encoding=utf-8 fileencoding=utf-8 showmode number noautoindent
set updatetime=80 ttimeoutlen=20
let s:sequence=0
let s:saves=0
let s:last=''
let s:ready=0
function! s:Publish(event, ...) abort
  if !s:ready | return | endif
  let shutting=filereadable($MQ3_VIM_CLOSING) || v:dying > 0
  if a:event ==# 'exit' && shutting | return | endif
  let mode=a:0 ? a:1 : strpart(mode(1),0,1)
  let state={'session':$MQ3_VIM_SESSION,'mode':mode,'line':line('.'),'column':strchars(strpart(getline('.'),0,col('.')-1))+1,'lines':getline(1,'$'),'modified':&modified ? v:true : v:false,'save_count':s:saves,'search':@/,'exited':a:event ==# 'exit' && !shutting ? v:true : v:false,'interactive':filereadable($MQ3_VIM_INPUT) ? v:true : v:false}
  let signature=json_encode(state)
  if signature ==# s:last && index(['ready','write','exit'],a:event)<0 | return | endif
  let s:last=signature
  let s:sequence+=1
  let state.sequence=s:sequence
  let state.event=a:event
  let raw=json_encode(state)
  call writefile([raw],$MQ3_VIM_EVENTS,'a')
  call writefile([raw],$MQ3_VIM_STATE.'.tmp')
  call rename($MQ3_VIM_STATE.'.tmp',$MQ3_VIM_STATE)
  if join(readfile($MQ3_VIM_ACTIVE),'') ==# $MQ3_VIM_SESSION
    call writefile([raw],$MQ3_VIM_RESUME.'.tmp')
    call rename($MQ3_VIM_RESUME.'.tmp',$MQ3_VIM_RESUME)
  endif
endfunction
function! s:Saved() abort
  let s:saves+=1
  call s:Publish('write')
endfunction
function! s:Start() abort
  let start=json_decode(join(readfile($MQ3_VIM_START),'\n'))
  if has_key(start,'lines')
    silent! %delete _
    call setline(1,empty(start.lines) ? [''] : start.lines)
    if get(start,'modified',v:false) | setlocal modified | else | setlocal nomodified | endif
    call cursor(get(start,'line',1),1)
    let chars=get(start,'column',1)-1
    let bytes=strlen(strcharpart(getline('.'),0,chars))
    call cursor(line('.'),bytes+1)
    let @/=get(start,'search','')
  endif
  let s:ready=1
  call s:Publish('ready','n')
  if exists('*timer_start') | call timer_start(80,{timer -> s:Publish('change')},{'repeat':-1}) | endif
  if get(start,'mode','n') ==# 'i'
    if get(start,'column',1) > strchars(getline('.')) | startinsert! | else | startinsert | endif
  endif
endfunction
augroup Mq3Practice
  autocmd!
  autocmd VimEnter * call <SID>Start()
  autocmd CursorMoved,CursorMovedI,TextChanged,TextChangedI * call <SID>Publish('change')
  autocmd InsertEnter * call <SID>Publish('mode','i')
  autocmd InsertLeave * call <SID>Publish('mode','n')
  autocmd BufWritePost * call <SID>Saved()
  autocmd VimLeavePre * call <SID>Publish('exit')
augroup END
