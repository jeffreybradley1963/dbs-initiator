package planner

import (
	"encoding/json"
	"fmt"
	"os"
	"time"
)

type Status string

const (
	StatusPending   Status = "Pending"
	StatusProcessed Status = "Processed"
	StatusComplete  Status = "Complete"
)

type StudyItem struct {
	Reference string    `json:"reference"`
	Title     string    `json:"title,omitempty"`
	Status    Status    `json:"status"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type StudyPlan struct {
	Items []StudyItem `json:"items"`
}

const planFileName = "study_plan.json"

func Load() (*StudyPlan, error) {
	file, err := os.ReadFile(planFileName)
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
	data, err := json.MarshalIndent(p, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(planFileName, data, 0644)
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

func (p *StudyPlan) GetNextPending() *StudyItem {
	for _, item := range p.Items {
		if item.Status == StatusPending {
			return &item
		}
	}
	return nil
}
