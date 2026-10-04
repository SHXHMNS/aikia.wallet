/**
 * Platform identity. Every product name, mark and contact shown in the software comes from here,
 * so a white-label deployment only needs different NEXT_PUBLIC_PLATFORM_* values (no code edits).
 */
export const platform = {
  name: process.env.NEXT_PUBLIC_PLATFORM_NAME || 'AIKIA.WALLET',
  shortName: process.env.NEXT_PUBLIC_PLATFORM_SHORT_NAME || 'AIKIA',
  mark: process.env.NEXT_PUBLIC_PLATFORM_MARK || 'a',
  supportEmail: process.env.NEXT_PUBLIC_PLATFORM_SUPPORT_EMAIL || 'connect@aikia.world',
};
