// 用途：验证内部服务令牌的签名、签发方、受众和有效期。
package auth

import (
	"errors"
	"strings"

	"github.com/golang-jwt/jwt/v5"
)

type Verifier struct {
	secret           []byte
	issuer, audience string
}

func NewVerifier(secret []byte, issuer, audience string) *Verifier {
	return &Verifier{secret: secret, issuer: issuer, audience: audience}
}
func (v *Verifier) Verify(raw string) (*Claims, error) {
	raw = strings.TrimSpace(raw)
	return v.parse(raw)
}

// 解析token
func (v *Verifier) parse(raw string) (*Claims, error) {
	claims := &Claims{}
	token, err := jwt.ParseWithClaims(raw, claims, func(t *jwt.Token) (interface{}, error) {
		if t.Method != jwt.SigningMethodHS256 {
			return nil, errors.New("only HS256 is accepted")
		}
		return v.secret, nil
	}, jwt.WithIssuer(v.issuer), jwt.WithAudience(v.audience), jwt.WithExpirationRequired())

	if err != nil || token == nil || !token.Valid {
		return nil, errors.New("invalid token")
	}
	c, ok := token.Claims.(*Claims)
	if !ok || c.Type != "service" || c.Subject == "" || c.ActorID == "" || c.WorkspaceID == "" || c.DatasourceID == "" {
		return nil, errors.New("required service claims are missing")
	}
	return c, nil
}
