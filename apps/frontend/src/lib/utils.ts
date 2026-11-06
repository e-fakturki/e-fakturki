export function toggleDarkMode() {
  document.documentElement.classList.toggle("prime-dark-mode");
}

export function formatLocalDate(date: Date) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");

  return `${yyyy}-${mm}-${dd}`;
}

export function formatDisplayDate(date: Date) {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");

  return `${yyyy}/${mm}/${dd}`;
}

export function parsePolishDateTime(value: string): Date {
  const [datePart, timePart] = value.split(", ");

  const [day, month, year] = datePart.split(".").map(Number);
  const [hours, minutes, seconds] = timePart.split(":").map(Number);

  return new Date(year, month - 1, day, hours, minutes, seconds);
}

export const formatPLN = (v: number) =>
  new Intl.NumberFormat("pl-PL", {
    style: "currency",
    currency: "PLN",
  }).format(v);

export function emptyToNull(value?: string | null | undefined) {
  return value === "" ? null : value;
}

export function roundTo2(value: number): number {
  return Math.round(value * 100) / 100;
}

export function calculateGrossPrice(netPrice: number, taxRate: number): number {
  return roundTo2(netPrice * (1 + taxRate));
}

export function calculateNetPrice(grossPrice: number, taxRate: number): number {
  return roundTo2(grossPrice / (1 + taxRate));
}

export function calculateGrossTotal(netPrice: number, amount: number, taxRate: number): number {
  return roundTo2(netPrice * amount * (1 + taxRate));
}

export function calculateNetTotal(netPrice: number, amount: number): number {
  return roundTo2(netPrice * amount);
}

export function calculateTaxTotal(netPrice: number, taxRate: number, amount: number): number {
  return roundTo2(netPrice * taxRate * amount);
}

export function verifyNetVsGrossPrice(
  netPrice: number | null,
  grossPrice: number | null,
  taxRate: number | null,
) {
  if (netPrice == null || grossPrice == null || taxRate == null) return true;

  const calculatedNet = calculateNetPrice(grossPrice, taxRate);
  const calculatedGross = calculateGrossPrice(netPrice, taxRate);

  return Math.abs(netPrice - calculatedNet) < 0.01 && Math.abs(grossPrice - calculatedGross) < 0.01;
}

export function verifyEntriesTotals(entry: {
  netPrice: number | null;
  amount: number | null;
  taxRate: number | null;
  grossTotal: number | null;
  netTotal: number | null;
  taxTotal: number | null;
}) {
  if (
    entry.netPrice == null ||
    entry.amount == null ||
    entry.taxRate == null ||
    entry.grossTotal == null ||
    entry.netTotal == null ||
    entry.taxTotal == null
  ) {
    return true;
  }

  const calculatedGrossTotal = calculateGrossTotal(entry.netPrice, entry.amount, entry.taxRate);
  const calculatedNetTotal = calculateNetTotal(entry.netPrice, entry.amount);
  const calculatedTaxTotal = calculateTaxTotal(entry.netPrice, entry.taxRate, entry.amount);

  return (
    Math.abs(entry.grossTotal - calculatedGrossTotal) < 0.01 &&
    Math.abs(entry.netTotal - calculatedNetTotal) < 0.01 &&
    Math.abs(entry.taxTotal - calculatedTaxTotal) < 0.01
  );
}

export function verifyInvoiceTotals(invoice: any) {
  const expected_gross_total = roundTo2(
    invoice.entries.reduce((acc, entry) => acc + entry.gross_total, 0),
  );
  const expected_tax_total = roundTo2(
    invoice.entries.reduce((acc, entry) => acc + entry.tax_total, 0),
  );
  const expected_net_total = roundTo2(
    invoice.entries.reduce((acc, entry) => acc + entry.net_total, 0),
  );
  return (
    Math.abs(invoice.gross_total - expected_gross_total) < 0.01 &&
    Math.abs(invoice.tax_total - expected_tax_total) < 0.01 &&
    Math.abs(invoice.net_total - expected_net_total) < 0.01
  );
}
