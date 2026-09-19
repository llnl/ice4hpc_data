find_package(PnetCDF QUIET)

# If find_package fails, create a fallback strategy
if(NOT PnetCDF_FOUND)
    # Allow the user to pass -DPNETCDF_DIR=/path/to/pnetcdf
    set(PNETCDF_DIR "" CACHE PATH "Path to PnetCDF installation prefix")
    
    find_path(PNETCDF_INCLUDE_DIR NAMES pnetcdf.h HINTS ${PNETCDF_DIR}/include)
    find_library(PNETCDF_LIBRARY NAMES pnetcdf HINTS ${PNETCDF_DIR}/lib)
    
    if(PNETCDF_INCLUDE_DIR AND PNETCDF_LIBRARY)
        add_library(PnetCDF::PnetCDF_C UNKNOWN IMPORTED)
        set_target_properties(PnetCDF::PnetCDF_C PROPERTIES
            INTERFACE_INCLUDE_DIRECTORIES "${PNETCDF_INCLUDE_DIR}"
            IMPORTED_LOCATION "${PNETCDF_LIBRARY}"
        )
    else()
        message(FATAL_ERROR "PnetCDF could not be found. Please set PNETCDF_DIR.")
    endif()
    set(PNETCDF_TARGET PnetCDF::PnetCDF_C)
endif()
