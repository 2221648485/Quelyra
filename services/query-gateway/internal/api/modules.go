package api

import "query-gateway/internal/auth"

type AppContext struct {
	verifier *auth.Verifier
}

func NewAppContext() *AppContext {
	verifier := auth.NewVerifier([]byte("11"), "11", "11")
	return &AppContext{
		verifier: verifier,
	}
}
