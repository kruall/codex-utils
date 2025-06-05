import { AppProps } from 'next/app'
import { TaskProvider } from '../context/TaskContext'
import { EpicProvider } from '../context/EpicContext'
import { AuthProvider } from '../context/AuthContext'
import { RepoProvider } from '../context/RepoContext'

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <RepoProvider>
        <EpicProvider>
          <TaskProvider>
            <Component {...pageProps} />
          </TaskProvider>
        </EpicProvider>
      </RepoProvider>
    </AuthProvider>
  )
}
