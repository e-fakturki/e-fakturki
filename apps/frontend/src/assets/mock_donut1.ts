const salesValue = 1000;
const productCount = 30;
const salesValueInCents = Math.round(salesValue * 100);
const weights = Array.from({ length: productCount }, () => Math.random());
const totalWeight = weights.reduce((sum, weight) => sum + weight, 0);
const exactValues = weights.map((weight) => (weight / totalWeight) * salesValueInCents);
const salesValuesInCents = exactValues.map(Math.floor);
const remainingCents =
  salesValueInCents - salesValuesInCents.reduce((sum, value) => sum + value, 0);

exactValues
  .map((value, index) => ({ index, fraction: value - Math.floor(value) }))
  .sort((left, right) => right.fraction - left.fraction)
  .slice(0, remainingCents)
  .forEach(({ index }) => salesValuesInCents[index]++);

const productSales = {
  year_number: 2026,
  month_number: 10,
  sales_value: salesValue,
  sales_distribution: Object.fromEntries(
    salesValuesInCents.map((value, index) => [`product${index + 1}`, value / 100]),
  ),
};

export default productSales;
