// Package credential 负责凭据的加密存储和使用。
package credential

type Cipher interface {
	// TODO: 使用 KMS 或信封加密；禁止明文持久化数据库凭据。
	Encrypt(plainText []byte) ([]byte, error)
	Decrypt(cipherText []byte) ([]byte, error)
}
