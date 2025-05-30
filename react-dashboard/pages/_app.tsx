import { AppProps } from 'next/app'
import { TaskProvider } from '../context/TaskContext'

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <TaskProvider>
      <Component {...pageProps} />
    </TaskProvider>
  )
} 