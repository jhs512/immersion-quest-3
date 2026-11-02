async function load() {
  await null;
  throw new Error('no data');
}
load();
console.log('after');
