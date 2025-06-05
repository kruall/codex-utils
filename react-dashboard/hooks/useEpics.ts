import { useEpicContext } from '../context/EpicContext'
import { Epic } from '../types'

export default function useEpics(): Epic[] {
  const { epics } = useEpicContext()
  return epics
}

