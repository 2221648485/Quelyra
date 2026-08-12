package telemetry

import (
	"log/slog"
	"os"
	"strings"
)

func InitLogger(env string) *slog.Logger {
	options := &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}

	var handler slog.Handler
	switch strings.ToLower(strings.TrimSpace(env)) {
	case "dev":
		handler = slog.NewTextHandler(os.Stdout, options)
	default:
		handler = slog.NewJSONHandler(os.Stdout, options)
	}

	logger := slog.New(handler)
	slog.SetDefault(logger)
	return logger
}
