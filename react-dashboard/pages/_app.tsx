import { AppProps } from 'next/app'
import { TaskProvider } from '../context/TaskContext'
import { EpicProvider } from '../context/EpicContext'
import { AuthProvider } from '../context/AuthContext'

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <EpicProvider>
        <TaskProvider>
          <Component {...pageProps} />
        </TaskProvider>
      </EpicProvider>
    </AuthProvider>
  )
}
