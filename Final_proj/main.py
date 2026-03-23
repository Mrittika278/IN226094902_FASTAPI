from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Online Learning Platform API",
    description="A simple API for managing courses and enrollments.",
    version="1.0.0",
)

class Course(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier for the course.",
        gt=0,
    )  # Example field constraint
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=500)
    instructor: str
    credits: int = Field(..., gt=0, le=10)
    is_active: bool = True

class Enrollment(BaseModel):
    id: int = Field(
        ...,
        description="Unique identifier for the enrollment.",
        gt=0,
    )
    course_id: int
    student_id: int
    enrollment_date: str  # Consider using datetime.date for real-world scenarios
    grade: Optional[float] = Field(
        None, gt=0, le=100
    )  # Optional field with constraints

# Mock database (replace with a real database in production)
courses = [
    Course(
        id=1,
        name="Introduction to Python",
        description="A beginner-friendly course on Python programming.",
        instructor="Jane Doe",
        credits=3,
    ),
    Course(
        id=2,
        name="Data Structures and Algorithms",
        description="Learn fundamental data structures and algorithms.",
        instructor="John Smith",
        credits=4,
    ),
]

enrollments = [
    Enrollment(id=1, course_id=1, student_id=101, enrollment_date="2023-01-15"),
    Enrollment(id=2, course_id=2, student_id=102, enrollment_date="2023-02-20"),
]

# Helper Functions
def find_course(course_id: int) -> Optional[Course]:
    """Finds a course by its ID."""
    for course in courses:
        if course.id == course_id:
            return course
    return None

def calculate_total_credits(course_ids: List[int]) -> int:
    """Calculates the total credits for a list of course IDs."""
    total_credits = 0
    for course_id in course_ids:
        course = find_course(course_id)
        if course:
            total_credits += course.credits
    return total_credits

def filter_courses(
    is_active: Optional[bool] = None, instructor: Optional[str] = None
) -> List[Course]:
    """Filters courses based on given criteria."""
    filtered_courses = courses
    if is_active is not None:
        filtered_courses = [
            course for course in filtered_courses if course.is_active == is_active
        ]
    if instructor is not None:
        filtered_courses = [
            course
            for course in filtered_courses
            if course.instructor.lower() == instructor.lower()
        ]
    return filtered_courses

# --- GET APIs ---
@app.get("/", status_code=status.HTTP_200_OK)
async def home():
    """Home route."""
    return {"message": "Welcome to the Online Learning Platform API!"}

@app.get("/courses/", response_model=List[Course], status_code=status.HTTP_200_OK)
async def list_courses():
    """Lists all courses."""
    return courses

@app.get(
    "/courses/{course_id}", response_model=Course, status_code=status.HTTP_200_OK
)
async def get_course(course_id: int):
    """Retrieves a course by its ID."""
    course = find_course(course_id)
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return course

@app.get("/courses/summary/count", status_code=status.HTTP_200_OK)
async def count_courses():
    """Returns the total number of courses."""
    return {"total_courses": len(courses)}

# --- POST API ---
@app.post(
    "/courses/", response_model=Course, status_code=status.HTTP_201_CREATED
)  # 201 Created
async def create_course(course: Course):
    """Creates a new course."""
    # Check if course ID already exists
    if find_course(course.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this ID already exists",
        )
    courses.append(course)
    return course

# --- PUT API ---
@app.put(
    "/courses/{course_id}", response_model=Course, status_code=status.HTTP_200_OK
)
async def update_course(course_id: int, course: Course):
    """Updates an existing course."""
    existing_course = find_course(course_id)
    if existing_course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Update the course (replace with more sophisticated update logic if needed)
    for i, c in enumerate(courses):
        if c.id == course_id:
            courses[i] = course
            return course
    return course

# --- DELETE API ---
@app.delete(
    "/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT
)  # 204 No Content
async def delete_course(course_id: int):
    """Deletes a course."""
    global courses
    original_length = len(courses)
    courses = [course for course in courses if course.id != course_id]
    if len(courses) == original_length:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )
    return  # No content to return

# --- Multi-Step Workflow (Example: Enrollment -> Grade -> Completion) ---
@app.post(
    "/enrollments/", response_model=Enrollment, status_code=status.HTTP_201_CREATED
)
async def create_enrollment(enrollment: Enrollment):
    """Enrolls a student in a course."""
    # Validation: Check if course exists
    if not find_course(enrollment.course_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Course not found"
        )

    enrollments.append(enrollment)
    return enrollment

@app.put(
    "/enrollments/{enrollment_id}/grade",
    response_model=Enrollment,
    status_code=status.HTTP_200_OK,
)
async def update_grade(enrollment_id: int, grade: float = Query(..., gt=0, le=100)):
    """Updates the grade for an enrollment."""
    for enrollment in enrollments:
        if enrollment.id == enrollment_id:
            enrollment.grade = grade
            return enrollment
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
    )

@app.post(
    "/enrollments/{enrollment_id}/complete", status_code=status.HTTP_200_OK
)  # No response model as it's just a confirmation
async def complete_enrollment(enrollment_id: int):
    """Marks an enrollment as complete (example)."""
    for enrollment in enrollments:
        if enrollment.id == enrollment_id:
            # In a real application, you might update a 'completed' flag in the enrollment record.
            return {"message": f"Enrollment {enrollment_id} marked as complete."}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
    )

# --- Advanced APIs ---
@app.get("/courses/search/", response_model=List[Course], status_code=status.HTTP_200_OK)
async def search_courses(
    keyword: Optional[str] = Query(None, description="Keyword to search for in course name or description"),
):
    """Searches courses by keyword."""
    if keyword is None:
        return courses

    keyword = keyword.lower()
    results = [
        course
        for course in courses
        if keyword in course.name.lower() or keyword in course.description.lower()
    ]
    return results

@app.get("/courses/sort/", response_model=List[Course], status_code=status.HTTP_200_OK)
async def sort_courses(
    sort_by: str = Query(
        "name", enum=["name", "instructor", "credits"], description="Field to sort by"
    ),
    order: str = Query(
        "asc", enum=["asc", "desc"], description="Sorting order (asc or desc)"
    ),
):
    """Sorts courses by a given field."""
    reverse = order == "desc"
    return sorted(courses, key=lambda course: getattr(course, sort_by), reverse=reverse)

@app.get("/courses/browse/", response_model=List[Course], status_code=status.HTTP_200_OK)
async def browse_courses(
    keyword: Optional[str] = Query(
        None, description="Keyword to search for in course name or description"
    ),
    sort_by: str = Query(
        "name", enum=["name", "instructor", "credits"], description="Field to sort by"
    ),
    order: str = Query(
        "asc", enum=["asc", "desc"], description="Sorting order (asc or desc)"
    ),
    page: int = Query(1, gt=0, description="Page number"),
    page_size: int = Query(10, gt=0, le=50, description="Number of items per page"),
):
    """Combined endpoint for browsing, searching, sorting, and paginating courses."""
    filtered_courses = courses

    if keyword is not None:
        keyword = keyword.lower()
        filtered_courses = [
            course
            for course in filtered_courses
            if keyword in course.name.lower() or keyword in course.description.lower()
        ]

    reverse = order == "desc"
    sorted_courses = sorted(
        filtered_courses, key=lambda course: getattr(course, sort_by), reverse=reverse
    )

    start = (page - 1) * page_size
    end = start + page_size
    paginated_courses = sorted_courses[start:end]

    return paginated_courses