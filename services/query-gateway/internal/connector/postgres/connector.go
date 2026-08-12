// 用途：实现 PostgreSQL 连接和受限查询执行能力。

package postgres

import (
	"query-gateway/internal/config"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

// 创建一个Postgres
func New(opts config.DatabaseConfig) (*gorm.DB, error) {
	db, err := gorm.Open(postgres.Open(opts.DSN), &gorm.Config{})
	if err != nil {
		return nil, err
	}

	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}

	sqlDB.SetMaxOpenConns(opts.MaxOpenConns)
	sqlDB.SetMaxIdleConns(opts.MaxIdleConns)

	return db, nil
}

// 关闭数据库连接池
func Close(db *gorm.DB) error {
	if db == nil {
		return nil
	}

	sqlDB, err := db.DB()
	if err != nil {
		return err
	}

	return sqlDB.Close()
}
