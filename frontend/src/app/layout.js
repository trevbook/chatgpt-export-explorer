import { AppRouterCacheProvider } from "@mui/material-nextjs/v15-appRouter";

export const metadata = {
  title: "ChatGPT Export Explorer",
  description: "Explore your exported ChatGPT data",
};

export default function RootLayout(props) {
  return (
    <html lang="en">
      <body>
        <AppRouterCacheProvider>{props.children}</AppRouterCacheProvider>
      </body>
    </html>
  );
}
