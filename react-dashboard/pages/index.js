import Navigation from '../components/Navigation'
import styles from './Page.module.css'

export default function Home() {
  return (
    <div className={styles.container}>
      <Navigation />
      <h1>Codex Dashboard</h1>
      <p>Select a view from the navigation menu.</p>
    </div>
  )
}
