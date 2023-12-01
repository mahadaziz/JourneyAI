import { Inter } from 'next/font/google'
import { ThemeProvider } from '../theme-provider'
import { getServerSession } from 'next-auth';
import { authOptions } from '../../api/auth/[...nextauth]/route';
import { AuthProvider } from "../../Providers";
import {SelectedColumnProvider} from "../../../context/SelectedColumnContext";
import '../../globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Data Driven Stories',
  description: '',
}

export default async function RootLayout({ children }) {
  // console.log(session);
  return (
    <html suppressHydrationWarning>
      <body>
        <ThemeProvider  attribute="class" defaultTheme="light" enableSystem>
          <AuthProvider>
            <SelectedColumnProvider>
              {children}
            </SelectedColumnProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}