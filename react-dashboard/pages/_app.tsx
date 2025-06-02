import { AppProps } from 'next/app'
import { TaskProvider } from '../context/TaskContext'
import { AuthProvider } from '../context/AuthContext'

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <TaskProvider>
        <Component {...pageProps} />
      </TaskProvider>
    </AuthProvider>
  )
}
