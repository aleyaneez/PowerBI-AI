export function parseFilename(filename: string): { company: string; week: string } {
  const pattern = /^(.*?)[-_](\d{4}-\d{2}-\d{2})\.pdf$/i;
  const match = filename.match(pattern);
  if (!match) {
    throw new Error(`El nombre del archivo no coincide con el formato esperado: ${filename}`);
  }
  return { company: match[1].toLowerCase(), week: match[2].toLowerCase() };
}