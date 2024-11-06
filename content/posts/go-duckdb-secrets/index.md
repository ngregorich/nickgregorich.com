---
title: "Go DuckDB Secrets"
date: 2024-11-05T17:45:19-08:00
description: "Using AWS secrets in DuckDB in Go"
categories: []
tags: ["go", "duckdb", "aws", "s3", "data"]
toc: true
math: false
draft: false
---
I didn't actually set out to learn Go, in fact this is essentially my Go *Hello World!*

However, the LLMs all provided legacy API results when asking them to use secrets in DuckDB in Go, so I thought I might try and set the record straight

## Background

The [DuckDB documentation](https://duckdb.org/docs/api/go) suggests using the 3rd party library [go-duckdb](https://github.com/marcboeker/go-duckdb) by Marc Boeker to interface to [database/sql](https://pkg.go.dev/database/sql) in Go. This is interesting for a couple of reasons:

1. I didn't realize that DuckDB does not have first party clients for all supported languages. You can take a look at the list of [Client APIs](https://duckdb.org/docs/api/overview.html) which looks like it has a maintainer name for 3rd party clients (a big thank you to Marc and all the other maintainers!)
2. Go has a standard database interface: [database/sql](https://pkg.go.dev/database/sql) which I haven't found to be the case in Python where I am using DuckDB, Snowflake, or InfluxDB each with its own specific interface
   1. A unified interface has obvious benefits of potentially being simpler and cleaner, but I hope there's still flexibility for interesting features like using secrets :)

## Using secrets

As mentioned, LLMs as of this writing recommend using the [Legacy Authentication Scheme for S3 API](https://duckdb.org/docs/extensions/httpfs/s3api_legacy_authentication.html). This does appear to still function today, but let's follow the documentation's recommendation:

> The recommended way to configuration and authentication of S3 endpoints is to use secrets.

and put an example using the preferred [S3 API Support](https://duckdb.org/docs/extensions/httpfs/s3api.html) on the web

### Code step by step

First, let's create a `go.mod` file

```go
module go_duck

go 1.22.8

require github.com/marcboeker/go-duckdb v1.8.2
```

Now, let's create `go_duck.go` and build it up step by step

1. Package declaration and import

```go
package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"

	_ "github.com/marcboeker/go-duckdb"
)
```
2. Read environment variables with `os.Getenv` 

```go
func main() {
	awsAccessKey := os.Getenv("AWS_ACCESS_KEY_ID")
	awsRegion := os.Getenv("AWS_REGION")
	awsSecretKey := os.Getenv("AWS_SECRET_ACCESS_KEY")

	if awsAccessKey == "" || awsRegion == "" || awsSecretKey == "" {
		log.Fatal("Required AWS environment variables not set. Please set AWS_ACCESS_KEY_ID, AWS_REGION, and AWS_SECRET_ACCESS_KEY")
	}
```

3. Use `sql.Open` to open a connection to DuckDB

```go
	db, err := sql.Open("duckdb", "")
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()
```

4. Write the query to set the secret (legacy and recommended)

**Legacy**

```go
    // Legacy way to set the S3 credentials
	secret_query := fmt.Sprintf("SET s3_access_key_id='%s'; SET s3_secret_access_key='%s'; SET s3_region='%s';",
		awsAccessKey, awsSecretKey, awsRegion)
```
**Recommended** (this line is the meat of the post)

```go
    // Recommended way to set the S3 credentials
	secret_query := fmt.Sprintf("CREATE SECRET secret1 (TYPE S3, KEY_ID '%s', SECRET '%s', REGION '%s');", awsAccessKey, awsSecretKey, awsRegion)
```

5. Run the secret query

```go
	_, err = db.Exec(secret_query)
	if err != nil {
		log.Fatal(err)
	}
```

6. Test the secret query by running a query on S3 data

**Note:** you'll need to edit `<my_bucket>` and `<my_object>`

```go
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
```

7. Print the results

```go
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
```

### Build and run

Like I said, I'm a Go noob, so I expect you know more than me at this point. In a terminal in the project directory:

1. Set up the dependencies

```bash
go mod tidy
```

2. Build the project

**Note:** I am running on an Apple Silicon MacBook Pro, so I am targeting `GOOS=darwin` and `GOARCH=arm64`. Be sure to set these to appropriate values

```bash
GOOS=darwin GOARCH=arm64 go build go_duck.go
```

3. Set up your environment variables, I use [Granted](https://www.granted.dev) from [Common Fate](https://www.commonfate.io)

```bash
assume default
```

4. Finally, run the binary

```bash
./go_duck
```

Go duck!

Here's the [go_duck.go](go_duck.go) code in its entirety

## Conclusion

Well, I couldn't find an example of using secrets in DuckDB in Go and now there is one! Hopefully this helps someone and hopefully someday an LLM will learn from this too :)
