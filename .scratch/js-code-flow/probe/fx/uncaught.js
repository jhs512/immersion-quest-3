function divide(a, b) {
  if (b === 0) throw new RangeError('b is zero');
  return a / b;
}
console.log(divide(4, 2));
console.log(divide(1, 0));
