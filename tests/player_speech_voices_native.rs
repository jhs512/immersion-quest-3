#![cfg(all(feature="desktop",debug_assertions))]
#[allow(dead_code)]
#[path="support/native_player.rs"] mod native_player;

// FNV-1a over (voice, NUL, text), as src/tts.rs names its cache files.
fn cache_name(voice:&str,text:&str)->String{
    let mut hash:u64=0xcbf29ce484222325;
    for byte in voice.bytes().chain([0u8]).chain(text.bytes()){hash^=byte as u64;hash=hash.wrapping_mul(0x100000001b3);}
    format!("{voice}-{hash:016x}.mp3")
}

#[test]
#[ignore="Requires an interactive desktop and internet access for Edge audio"]
fn java_examples_reach_the_neural_and_device_voices_as_converted_text(){
    let session=molip_quest::pilot_session::PilotSession::new().unwrap();
    let mut command=std::process::Command::new(env!("CARGO_BIN_EXE_molip-quest"));
    native_player::configure(&session,&mut command,"speech-voices");
    command.env("MOLIP_PILOT_SELF_TEST","speech-voices");
    let status=native_player::wait(&mut command.spawn().unwrap(),120,"speech-voices");
    let raw=std::fs::read_to_string("target/pilot-native-result.json").unwrap();
    std::fs::copy("target/pilot-native-result.json","target/pilot-speech-voices-native-result.json").unwrap();
    let result:serde_json::Value=serde_json::from_str(&raw).unwrap();
    assert!(status.success()&&result["passed"]==true,"{result}");
    // The native TTS service cached each clip under the converted text, not the written one.
    let cache=session.directory().join("tts-cache");
    let found:Vec<String>=std::fs::read_dir(&cache).map(|d|d.filter_map(|e|e.ok()).map(|e|e.file_name().to_string_lossy().into_owned()).collect()).unwrap_or_default();
    for clip in result["neural"].as_array().unwrap(){
        let name=cache_name("ko-KR-SunHiNeural",clip["expected"].as_str().unwrap());
        let written=cache_name("ko-KR-SunHiNeural",clip["source"].as_str().unwrap());
        assert!(found.contains(&name),"{name} not in {cache:?}: {found:?}");
        assert!(!found.contains(&written),"the written form was sent: {written}");
    }
}
