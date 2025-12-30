# Eric Araújo - Academic Website

This is the source code for Eric Araújo's personal academic website, built with the **MyST Document Engine**.

## 🎯 About

This website showcases the academic work and Christian scholarship of Eric Araújo, Associate Professor in the Computer Science Department at Calvin University. The site emphasizes the integration of Reformed faith with rigorous academic inquiry across all areas of teaching, research, and service.

## 🚀 Built With

- **MyST** - Modern documentation and publishing platform
- **MyST Markdown** - Enhanced markdown with rich features
- **Node.js** - MyST CLI runtime

## 🏗️ Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Setup

1. Clone the repository:

```bash
git clone https://github.com/ericaraujophd/ericaraujophd.github.io.git
cd ericaraujophd.github.io
```

2. Install MyST CLI:

```bash
npm install -g mystmd
```

3. Start development server:

```bash
myst start --port 3001
```

The site will be available at `http://localhost:3001`

## 📁 Structure

```
├── myst.yml                 # MyST configuration
├── index.md                 # Homepage with academic overview
├── publications/            # Time-clustered publications (2015-2019, 2020-2024, 2025-2029)
├── advising/               # Student advising (current/past)
├── teaching.md             # Teaching philosophy and courses
├── presentations.md        # Conference presentations
├── updates.md              # News and announcements
├── cfr.html               # Calvin Faith Reader tool
├── schedule.html          # Academic schedule
├── files/                 # Documents and assets
├── images/                # Image resources
└── cv/                    # Curriculum vitae
```

## ✨ Features

- **MyST Admonitions** - Rich content blocks (notes, tips, warnings, etc.)
- **Hierarchical Navigation** - Organized content structure
- **Responsive Design** - Works on all devices
- **Faith Integration** - Balanced Reformed Christian perspective
- **Academic Focus** - Publications, teaching, and research showcase
- **DOI Integration** - Automatic DOI linking for publications

## 🛠️ Building

To build the site for production:

```bash
myst build --html
```

Built files will be in `_build/site/`

## 📝 Content Management

### Publications
Publications are organized by 5-year periods in the `publications/` directory for better navigation and maintenance.

### Advising
Student information is organized hierarchically with current and past advisees for privacy and organization.

### Navigation
The site includes custom navigation actions:
- ✝️ CFR Generator - Calvin Faith Reader tool
- 📅 Schedule - Academic calendar
- GitHub - Source code repository

## 🤝 Contributing

This is a personal academic website. For suggestions or corrections, please open an issue.

## 📄 License

Content is licensed under [Creative Commons Attribution Share Alike 4.0 International](LICENSE.md).

## 🔗 Links

- **Live Site**: [ericaraujophd.github.io](https://ericaraujophd.github.io)
- **Calvin University**: [calvin.edu](https://calvin.edu)
- **Computer Science Department**: [calvin.edu/academics/departments-programs/computer-science](https://calvin.edu/academics/departments-programs/computer-science)

---

> "In the great theater of human life it is only to God and the angels that we ought to play our parts." - **John Calvin**
