from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from . import models
import json
from django.http import JsonResponse

# Serializers
from .serializers import CategorySerializer

# Models
from .models import Category

@api_view(['GET', 'POST'])
def Category_List(request):
	if request.method == 'GET':
		categories = Category.objects.all()
		serializer = CategorySerializer(categories, many=True)
		return Response(serializer.data)


	elif request.method == 'POST':
		serializer = CategorySerializer(data=request.data)

		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=201) # 201 Created
		return Response(serializer.errors, status=400) # Forbidden

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def Category_Detail(request, pk):
	try:
		category = Category.objects.get(pk=pk)
		serializer = CategorySerializer(category, many=False)
		#return Response(serializer.data, status=200)
	except Category.DoesNotExist:
		return Response({"response": f"The resource with id {pk} does not exist"},status=404)

	if request.method == 'GET':
		category = Category.objects.get(pk=pk)
		serializer = CategorySerializer(category, many=False)

		return Response(serializer.data, status=200)

	elif request.method == 'PUT':
		# Serialize the request data using (data=request.data) and pass in "category" so that DRF knows which instance to replace
		serializer = CategorySerializer(category, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer, status)
		return Response(serializer.errors, status=400)


	elif request.method == 'PATCH':
		# Serialize the request data using (data=request.data) and pass in "category" so that DRF knows which instance to replace
		serializer = CategorySerializer(category, data=request.data, partial=True) # Partial => Only replace the requested fields
		if serializer.is_valid():
			serializer.save()
			return Response(serializer, status)
		return Response(serializer.errors, status=400)

	elif request.method == 'DELETE':
		category.delete()
		return Response(status=204) # 204 No Content	
		
