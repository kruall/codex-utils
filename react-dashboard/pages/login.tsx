import Navigation from '../components/Navigation'
import styles from './Page.module.css'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { token, login, logout } = useAuth()

  return (
    <div className={styles.container}>
      <Navigation />
      <h1>Authentication</h1>
      {token ? (
        <>
          <p>You are logged in.</p>
          <button onClick={logout}>Logout</button>
        </>
      ) : (
        <>
          <p>You are not logged in.</p>
          <button onClick={login}>Login with GitHub</button>
        </>
      )}
    </div>
  )
}
