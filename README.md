# cogniflow
Cogniflow improves student efficiency by using AI to personalize learning, track progress, and identify knowledge gaps in real time. It helps students study smarter by giving targeted practice, reducing revision time, and focusing only on topics they struggle.  
Many students suffer from 'The Illusion of Competence,' where they spend 10+ hours studying but retain less than 20% of the material due to cognitive fatigue and passive learning. Current tools only track time (how long you study) or performance (what you score), but never the correlation between the two. This disconnect leads to burnout, inefficient schedule planning, and poor academic outcomes despite high effort. Students need a way to identify their 'Cognitive Ceiling'—the point where extra study hours become counterproductive.

Who It's For
  -University students in high-intensity majors (Medicine, Law, STEM).
  -Competitive exam candidates (GRE, MCAT, LSAT) prepping for several months.
  -Educational consultants looking for objective data on student fatigue and optimal study patterns.
  
Core Features:
1:Diminishing Returns Tracker:- A centralized dashboard that calculates the 'Retention-per-Hour' (RPH) metric. It visualizes the delta between total hours studied and exam/quiz performance, identifying the exact hour where learning efficiency drops by more than 30%.
2:Passive-to-Active Ratio Analyzer:- A tool that ingest YouTube watch history and Pomodoro logs to categorize study materials into 'Active' vs 'Passive' learning. It uses a weighted scoring system to show how much 'Passive' consumption contributes to actual quiz success.
3:Burnout Detection Engine:- An automated reporting system that flags patterns of 'False Productivity' (long hours with high error rates). It generates a 'Rest Requirement' alert when it detects three consecutive sessions of declining performance.
4:Unified Learning Data Pipeline:- A multi-source data importer that allows students to upload CSVs from pomodoro apps, manual study logs, and Quizlet results. It cleanses and joins these disparate datasets into a unified longitudinal study record.

KPIs (Key Performance Indicators)
1. Retention %: Average score across all assessments.
2. RPH (Retention Per Hour): Points scored per hour of study invested.
3. Active Learning Ratio: Percentage of total study time spent on "Active" methods.
4. The "Cognitive Ceiling": The hour mark where performance drops by >30%.
5. False Productivity Hours: Hours spent in "Passive" modes with low Focus Scores.
6. Burnout Risk Index: A 0-100 score based on declining performance over consecutive days.

DAX Measures
dax
•- 1. Total Retention Rate
Avg Retention % = DIVIDE(SUM(FactAssessments[Questions_Correct]), SUM(FactAssessments[Questions_Total]), 0)
•- 2. Study Duration (Hours)
Total Study Hours = SUM(FactSessions[Duration_Minutes]) / 60
•- 3. Retention per Hour (RPH)
RPH = DIVIDE([Avg Retention %] * 100, [Total Study Hours], 0)
•- 4. Passive-to-Active Ratio
Active Ratio =
VAR ActiveHours = CALCULATE([Total Study Hours], DimMethods[StrategyType] = "Active")
RETURN DIVIDE(ActiveHours, [Total Study Hours], 0)
•- 5. Efficiency Delta (To find the "Ceiling")
•- Measures performance of the current session vs the average
Efficiency Delta =
VAR GlobalAvg = AVERAGEX(ALL(FactAssessments), [Avg Retention %])
RETURN [Avg Retention %] - GlobalAvg
•- 6. Burnout Alert (Boolean Logic)
Burnout Alert =
IF([Avg Retention %] < 0.6 && [Total Study Hours] > 6, "High Risk", "Optimal")
