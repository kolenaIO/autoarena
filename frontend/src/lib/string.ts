export function pluralize(count: number, noun: string, suffix = 's') {
  return `${count.toLocaleString()} ${noun}${count !== 1 ? suffix : ''}`;
}
