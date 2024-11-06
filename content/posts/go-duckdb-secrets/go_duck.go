package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/marcboeker/go-duckdb"
)

func main() {
	awsAccessKey := os.Getenv("AWS_ACCESS_KEY_ID")
	awsRegion := os.Getenv("AWS_REGION")
	awsSecretKey := os.Getenv("AWS_SECRET_ACCESS_KEY")

	if awsAccessKey == "" || awsRegion == "" || awsSecretKey == "" {
		log.Fatal("Required AWS environment variables not set. Please set AWS_ACCESS_KEY_ID, AWS_REGION, and AWS_SECRET_ACCESS_KEY")
	}

	db, err := sql.Open("duckdb", "")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Legacy way to set the S3 credentials
	secret_query := fmt.Sprintf("SET s3_access_key_id='%s'; SET s3_secret_access_key='%s'; SET s3_region='%s';",
		awsAccessKey, awsSecretKey, awsRegion)

	_, err = db.Exec(secret_query)
	if err != nil {
		log.Fatal(err)
	}

	type ColumnInfo struct {
		ColumnName string
		ColumnType string
		IsNullable string
		Key        sql.NullString
		Default    sql.NullString
		Extra      sql.NullString
	}

	rows, err := db.Query("describe from read_parquet('s3://<my_bucket>/<my_object>.parquet')")
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	var columns []ColumnInfo

	for rows.Next() {
		var col ColumnInfo
		err := rows.Scan(
			&col.ColumnName,
			&col.ColumnType,
			&col.IsNullable,
			&col.Key,
			&col.Default,
			&col.Extra,
		)
		if err != nil {
			log.Fatal(err)
		}
		columns = append(columns, col)
	}

	for _, col := range columns {
		fmt.Printf("Column: %s, Type: %s, Nullable: %s\n",
			col.ColumnName, col.ColumnType, col.IsNullable)
	}
}
