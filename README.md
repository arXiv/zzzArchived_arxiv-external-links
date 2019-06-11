# arxiv-external-links
Clearinghouse for relations between arXiv e-prints and external resources

## Background
A wide range of requirements and feature requests that we have received from stakeholders and end users involve attaching relational metadata to arXiv e-prints. This includes things like links to datasets, code, and other online content, and better support for information about the published version of record. Including this kind of relational metadata in the core arXiv metadata record is a poor fit given the way that e-prints are versioned, the requirement that secondary metadata be maintainable outside of the submission process, and the requirement that support for secondary metadata be as evolvable and extensible as possible. Additionally, we need to bring forward into NG the automated routines that we use to harvest relational metadata (e.g. DOIs, journal citations) from other publishing platforms; a shortcoming of the classic system is that the provenance of these kinds of metadata are not tracked, which presents challenges for our partners to interpret and use those metadata downstream.

Our goal is to support the accession, display, and reuse of secondary metadata by implementing a separate data structure and backend service.

We will implement a service that handles secondary metadata, starting with improved support for information about a paper’s version of record. 

As part of this work, we will reimplement the harvesting routines that collect metadata from external sources to enhance arXiv secondary metadata. This service will be accessible via the arXiv API Gateway.

We will extend the service to support addition of author-curated links by paper-owners, and display those links on the abstract page.

We will extend the service to support additional high-value metadata elements, based on input from member institutions and other stakeholders.
