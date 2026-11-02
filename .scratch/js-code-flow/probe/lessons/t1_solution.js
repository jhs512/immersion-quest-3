// 준비 값: 변형 검사에서 값이 달라져요.
const VALUE = 6;
const events = [];
function ping() { events.push("ping"); }
setImmediate(ping);
events.push("계산 " + VALUE);
setImmediate(() => console.log(events.join(" -> ")));
