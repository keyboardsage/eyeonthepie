package main

import (
	"bufio"
	_ "embed"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

//go:embed template.html
var template string

func escapeSingleQuotes(input string) string {
	var escaped strings.Builder

	for _, r := range input {
		if r == '\'' {
			escaped.WriteRune('\\')
		}
		escaped.WriteRune(r)
	}

	return escaped.String()
}

func main() {
	// Read sender_addresses.txt
	file, err := os.Open("sender_addresses.txt")
	if err != nil {
		fmt.Printf("Error opening file: %v\n", err)
		return
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	var emailAddresses []string
	for scanner.Scan() {
		emailAddresses = append(emailAddresses, scanner.Text())
	}

	if err := scanner.Err(); err != nil {
		fmt.Printf("Error reading file: %v\n", err)
		return
	}

	// Sort email addresses
	sort.Strings(emailAddresses)

	// Count unique occurrences and save to a map
	emailCounts := make(map[string]int)
	for _, email := range emailAddresses {
		emailCounts[email]++
	}

	// Invert the map to have counts as keys
	counts := make(map[int][]string)
	for email, count := range emailCounts {
		counts[count] = append(counts[count], email)
	}

	// Get all unique counts and sort them in descending order
	var uniqueCounts []int
	for count := range counts {
		uniqueCounts = append(uniqueCounts, count)
	}
	sort.Sort(sort.Reverse(sort.IntSlice(uniqueCounts)))

	// Accumulate the top 25 highest counts and associated email addresses, in text and HTML
	var output strings.Builder
	var outputHTML strings.Builder
	var emailAddressToEncode string
	for i, count := range uniqueCounts {
		if i >= 25 {
			break
		}

		// Text
		output.WriteString(fmt.Sprintf("%d: %v\n", count, counts[count]))

		// Email
		emailAddressToEncode = fmt.Sprintf("%v", counts[count]);
		outputHTML.WriteString(fmt.Sprintf("['%v', %d],\n", escapeSingleQuotes(emailAddressToEncode), count))
	}

	// Remove the trailing comma 
	var outputHTMLWithoutComa string
	outputHTMLWithoutComa = outputHTML.String()
	outputHTMLWithoutComa = outputHTMLWithoutComa[:len(outputHTMLWithoutComa)-1]

	// Print the accumulated output
	fmt.Print(output.String())

	// Replace the placeholders with the output values and save to file
	pieHTML := strings.Replace(template, "~1~", outputHTMLWithoutComa, 1)
	pieHTML = strings.Replace(pieHTML, "~2~", output.String(), 1)
	//DEBUG: fmt.Print(pieHTML)
	pieFilename := "pie.html"
	err = ioutil.WriteFile(pieFilename, []byte(pieHTML), 0644)
	if err != nil {
		log.Fatalf("Failed to write to the file: %v", err)
	} else {
		fmt.Printf("Successfully saved the pie chart to the file %v.", pieFilename)

		// Tell them which file to view in their browser
		wd, err := os.Getwd()
		if err != nil {
			panic(err)
		}
		path := filepath.Join(wd, "pie.html")
		url := "file://" + path
		fmt.Println("Open the file %v in your preferred web browser.", url)
	}
}

