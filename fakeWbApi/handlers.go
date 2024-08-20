package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

var client *mongo.Client

func connectToDb(URI string) *mongo.Client {

	opts := options.Client().ApplyURI(URI)
	client, _ = mongo.Connect(context.TODO(), opts)

	fmt.Println("Connected")
	return client
}

func getMainHandler(w http.ResponseWriter, r *http.Request) {
	coll := client.Database("wbFakeData").Collection("wbFakeData_data")
	cursor, err := coll.Find(context.TODO(), bson.D{})

	if err != nil {
		http.Error(w, "Failed to fetch data", http.StatusInternalServerError)
		return
	}

	defer cursor.Close(context.TODO())

	var results []fakeWbApiData

	if err := cursor.All(context.TODO(), &results); err != nil {
		http.Error(w, "Failed to parse data", http.StatusInternalServerError)
		return
	}

	jsonData, err := json.Marshal(results)

	if err != nil {
		http.Error(w, "Failed to marshal data", http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.Write(jsonData)
}
