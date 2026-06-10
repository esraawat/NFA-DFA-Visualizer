import { useMutation } from '@tanstack/react-query'
import axios from 'axios'

const BASE = '/api'

export function useConverter() {
  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await axios.post(`${BASE}/convert`, payload)
      return data
    },
  })
}

export function useSimulate() {
  return useMutation({
    mutationFn: async (payload) => {
      const { data } = await axios.post(`${BASE}/simulate`, payload)
      return data
    },
  })
}
