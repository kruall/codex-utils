import { TaskProvider } from '../context/TaskContext'

export default function MyApp({ Component, pageProps }) {
  return (
    <TaskProvider>
      <Component {...pageProps} />
    </TaskProvider>
  )
}
