import { renderHook, waitFor } from '@testing-library/react'
import { useAsync } from './useAsync'

describe('useAsync', () => {
  it('starts in loading state and resolves with data', async () => {
    const fetcher = vi.fn().mockResolvedValue({ value: 42 })

    const { result } = renderHook(() => useAsync(fetcher, []))

    expect(result.current.loading).toBe(true)

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.data).toEqual({ value: 42 })
    expect(result.current.error).toBeNull()
  })

  it('captures the error message on rejection', async () => {
    const fetcher = vi.fn().mockRejectedValue(new Error('network down'))

    const { result } = renderHook(() => useAsync(fetcher, []))

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.error).toBe('network down')
    expect(result.current.data).toBeNull()
  })

  it('refetches when reload is called', async () => {
    const fetcher = vi.fn().mockResolvedValueOnce({ value: 1 }).mockResolvedValueOnce({ value: 2 })

    const { result } = renderHook(() => useAsync(fetcher, []))
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.data).toEqual({ value: 1 })

    result.current.reload()

    await waitFor(() => expect(result.current.data).toEqual({ value: 2 }))
    expect(fetcher).toHaveBeenCalledTimes(2)
  })

  it('refetches when a dependency changes', async () => {
    const fetcher = vi.fn().mockResolvedValueOnce({ value: 1 }).mockResolvedValueOnce({ value: 2 })

    const { result, rerender } = renderHook(({ dep }) => useAsync(fetcher, [dep]), {
      initialProps: { dep: 1 },
    })
    await waitFor(() => expect(result.current.loading).toBe(false))

    rerender({ dep: 2 })

    await waitFor(() => expect(result.current.data).toEqual({ value: 2 }))
    expect(fetcher).toHaveBeenCalledTimes(2)
  })
})
