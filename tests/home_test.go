package tests

import (
	"sis2/fixtures"
	"testing"
)

func TestHomePageLoads(t *testing.T) {
	homePage := fixtures.NewHomePage(t)
	if err := homePage.Open(); err != nil {
		t.Fatalf("open homepage: %v", err)
	}
	if err := homePage.ExpectLoaded(); err != nil {
		t.Fatalf("homepage expectloaded: %v", err)
	}
}
