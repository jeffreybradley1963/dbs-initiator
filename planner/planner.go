package planner

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

type Status string

const (
	StatusPending   Status = "Pending"
	StatusProcessed Status = "Processed"
	StatusComplete  Status = "Complete"
)

type GeneratedImage struct {
	Filename    string `json:"filename"`
	VerseRange  string `json:"verse_range"`
	Description string `json:"description"`
}

type StudyItem struct {
	Reference       string           `json:"reference"`
	Title           string           `json:"title,omitempty"`
	Status          Status           `json:"status"`
	GeneratedImages []GeneratedImage `json:"generated_images,omitempty"`
	CreatedAt       time.Time        `json:"created_at"`
	UpdatedAt       time.Time        `json:"updated_at"`
}

type StudyPlan struct {
	Items []StudyItem `json:"items"`
}

const planDirName = ".dbs-initiator"
const planFileName = "study_plan.json"

func getPlanPath() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", fmt.Errorf("could not find home directory: %w", err)
	}
	return filepath.Join(home, planDirName, planFileName), nil
}

func Load() (*StudyPlan, error) {
	path, err := getPlanPath()
	if err != nil {
		return nil, err
	}

	file, err := os.ReadFile(path)
	if os.IsNotExist(err) {
		return &StudyPlan{Items: []StudyItem{}}, nil
	}
	if err != nil {
		return nil, err
	}

	var plan StudyPlan
	if err := json.Unmarshal(file, &plan); err != nil {
		return nil, err
	}
	return &plan, nil
}

func (p *StudyPlan) Save() error {
	path, err := getPlanPath()
	if err != nil {
		return err
	}

	// Ensure directory exists
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return fmt.Errorf("failed to create config directory: %w", err)
	}

	data, err := json.MarshalIndent(p, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, data, 0644)
}

func (p *StudyPlan) Add(reference string) error {
	// Check if already exists
	for _, item := range p.Items {
		if item.Reference == reference {
			return fmt.Errorf("reference '%s' already exists in plan", reference)
		}
	}

	newItem := StudyItem{
		Reference: reference,
		Status:    StatusPending,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}
	p.Items = append(p.Items, newItem)
	return p.Save()
}

func (p *StudyPlan) List() []StudyItem {
	return p.Items
}

func (p *StudyPlan) UpdateStatus(reference string, status Status) error {
	for i, item := range p.Items {
		if item.Reference == reference {
			p.Items[i].Status = status
			p.Items[i].UpdatedAt = time.Now()
			return p.Save()
		}
	}
	return fmt.Errorf("reference '%s' not found in plan", reference)
}

func (p *StudyPlan) UpdateTitle(reference, title string) error {
	for i, item := range p.Items {
		if item.Reference == reference {
			p.Items[i].Title = title
			p.Items[i].UpdatedAt = time.Now()
			return p.Save()
		}
	}
	return fmt.Errorf("reference '%s' not found in plan", reference)
}

func (p *StudyPlan) UpdateImages(reference string, images []GeneratedImage) error {
	for i, item := range p.Items {
		if item.Reference == reference {
			p.Items[i].GeneratedImages = images
			p.Items[i].UpdatedAt = time.Now()
			return p.Save()
		}
	}
	return fmt.Errorf("reference '%s' not found in plan", reference)
}

func (p *StudyPlan) GetNextPending() *StudyItem {
	for _, item := range p.Items {
		if item.Status == StatusPending {
			return &item
		}
	}
	return nil
}
