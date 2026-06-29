import { http, HttpResponse } from 'msw'
import { server } from '../test/server'
import { apiClient, ApiError } from './client'

describe('apiClient.get', () => {
  it('returns the parsed JSON body on success', async () => {
    server.use(
      http.get('/api/users/1', () => HttpResponse.json({ id: 1, name: 'Ana' })),
    )

    const result = await apiClient.get<{ id: number; name: string }>('/users/1')

    expect(result).toEqual({ id: 1, name: 'Ana' })
  })

  it('throws ApiError with the status code on a 404', async () => {
    server.use(
      http.get('/api/users/99', () =>
        HttpResponse.json({ detail: 'User not found' }, { status: 404 }),
      ),
    )

    await expect(apiClient.get('/users/99')).rejects.toMatchObject({
      status: 404,
      name: 'ApiError',
    })
  })

  it('is an instance of ApiError', async () => {
    server.use(
      http.get('/api/boom', () => HttpResponse.json({ detail: 'oops' }, { status: 500 })),
    )

    await expect(apiClient.get('/boom')).rejects.toBeInstanceOf(ApiError)
  })
})

describe('apiClient.post', () => {
  it('sends a JSON body and returns the parsed response', async () => {
    server.use(
      http.post('/api/users', async ({ request }) => {
        const body = await request.json()
        return HttpResponse.json({ id: 1, ...(body as object) }, { status: 201 })
      }),
    )

    const result = await apiClient.post<{ id: number; name: string }>('/users', {
      name: 'Bia',
    })

    expect(result).toEqual({ id: 1, name: 'Bia' })
  })

  it('throws ApiError when validation fails with a 422', async () => {
    server.use(
      http.post('/api/users', () =>
        HttpResponse.json({ detail: [{ msg: 'field required' }] }, { status: 422 }),
      ),
    )

    await expect(apiClient.post('/users', {})).rejects.toMatchObject({ status: 422 })
  })
})
