// 준비 값: 변형 검사에서 값이 달라져요.
const VALUE = 6;
const events = [];
async function heavy() {
    Promise.resolve();
    events.push("계산 " + VALUE);
}
heavy();
events.push("ping");
setImmediate(() => console.log(events.join(" -> ")));
