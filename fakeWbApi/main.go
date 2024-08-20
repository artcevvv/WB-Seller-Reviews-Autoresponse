package main

import (
	"fmt"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
)

func main() {
	r := chi.NewRouter()

	mongoUri := "mongodb+srv://artcevvv:3Ovw2HRpJObudkcG@reviews.jbdvt.mongodb.net/?retryWrites=true&w=majority&appName=Reviews"

	connectToDb(mongoUri)

	r.Use(middleware.Logger)
	r.Use(cors.AllowAll().Handler)

	r.Get("/", getMainHandler)
	// r.Post("/", postMainHandler)

	fmt.Println("http://localhost:4001")
	http.ListenAndServe(":4001", r)

}
