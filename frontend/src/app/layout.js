export const metadata = {
  title: "ChatGPT Export Explorer",
  description: "Explore your exported ChatGPT data",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
